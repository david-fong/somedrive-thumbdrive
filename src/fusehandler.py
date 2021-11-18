#!/usr/bin/env python
# from __future__ import print_function, absolute_import, division

import logging
import os
import pathlib
from Crypto.Cipher import ChaCha20

from errno import EACCES
import threading

import psutil
import fuse



class CrytoOperations(fuse.LoggingMixIn, fuse.Operations):
    """
    https://libfuse.github.io/doxygen/structfuse__operations.html
    """
    def __init__(self, root, key: bytearray):
        # TODO throw if brand file is missing or key does not hash to its contents

        self.root = os.path.realpath(root)
        self.key = key
        self.rwlock = threading.Lock()

    def __call__(self, op, path, *args):
        return super(CrytoOperations, self).__call__(op, self.root + path, *args)

    def access(self, path, mode):
        if not os.access(path, mode):
            raise fuse.FuseOSError(EACCES)

    chmod = os.chmod
    chown = os.chown

    def create(self, path, mode):
        return os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, mode)

    def flush(self, path, fh):
        return os.fsync(fh)

    def fsync(self, path, datasync, fh):
        if datasync != 0:
            return os.fdatasync(fh)
        else:
            return os.fsync(fh)

    def getattr(self, path, fh=None):
        st = os.lstat(path)
        return dict((key, getattr(st, key)) for key in (
            'st_atime', 'st_ctime', 'st_gid', 'st_mode', 'st_mtime',
            'st_nlink', 'st_size', 'st_uid')) # do we need 'std_blocks'?

    getxattr = None

    def link(self, target, source):
        return os.link(self.root + source, target)

    listxattr = None
    mkdir = os.mkdir
    mknod = os.mknod
    open = os.open

    def read(self, path, size, offset, fh):
        with self.rwlock:
            os.lseek(fh, offset, 0)
            plain_chunk = os.read(fh, size)
            cipher = ChaCha20.new(key=self.key, nonce=b"aaaaaaaaaaaa")
            cipher_chunk = cipher.decrypt(plain_chunk)
            return cipher_chunk
            # return plain_chunk

    def readdir(self, path, fh):
        return ['.', '..'] + os.listdir(path)

    readlink = os.readlink

    def release(self, path, fh):
        return os.close(fh)

    def rename(self, old, new):
        return os.rename(old, self.root + new)

    rmdir = os.rmdir

    def statfs(self, path):
        stv = os.statvfs(path)
        return dict((key, getattr(stv, key)) for key in (
            'f_bavail', 'f_bfree', 'f_blocks', 'f_bsize', 'f_favail',
            'f_ffree', 'f_files', 'f_flag', 'f_frsize', 'f_namemax'))

    def symlink(self, target, source):
        return os.symlink(source, target)

    def truncate(self, path, length, fh=None):
        with open(path, 'r+') as f:
            f.truncate(length)

    unlink = os.unlink
    utimens = os.utime

    def write(self, path, data, offset, fh):
        with self.rwlock:
            os.lseek(fh, offset, 0)
            plain_chunk = data
            cipher = ChaCha20.new(key=self.key, nonce=b"aaaaaaaaaaaa")
            encrypted_chunk = cipher.encrypt(plain_chunk)
            return os.write(fh, encrypted_chunk)
            #return os.write(fh, data)


def open_fuse(root: str, mount: str, key: bytearray) -> fuse.FUSE:
    # TODO throw if realpath of root is inside mount
    return fuse.FUSE(CrytoOperations(root, key), mount, foreground=True, allow_other=False)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('root')
    parser.add_argument('mount')
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)
    fuse_ = open_fuse(args.root, args.mount)