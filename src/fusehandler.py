#!/usr/bin/env python
# from __future__ import print_function, absolute_import, division

import errno
import logging
import os
from pathlib import Path
import threading

import secrets
from Crypto.Cipher import ChaCha20
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
			raise fuse.FuseOSError(errno.EACCES)

	chmod = os.chmod
	chown = os.chown

	def create(self, path, mode):
		fh = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, mode)
		nonce = secrets.token_bytes(24)
		os.write(fh, nonce)
		os.lseek(fh, 0, os.SEEK_SET)
		return fh

	def flush(self, path, fh):
		return os.fsync(fh)

	def fsync(self, path, datasync, fh):
		if datasync != 0:
			return os.fdatasync(fh)
		else:
			return os.fsync(fh)

	def getattr(self, path, fh=None):
		st = dict((key, getattr(os.lstat(path), key)) for key in (
			'st_atime', 'st_ctime', 'st_gid', 'st_mode', 'st_mtime',
			'st_nlink', 'st_size', 'st_uid')) # do we need 'std_blocks'?
		st['st_size'] = st['st_size'] - 24
		return st

	getxattr = None

	def link(self, target, source):
		return os.link(self.root + source, target)

	listxattr = None
	mkdir = os.mkdir
	mknod = os.mknod
	open = os.open

	def read(self, path, size, offset, fh):
		with self.rwlock:
			os.lseek(fh, -24, os.SEEK_END)
			nonce = os.read(fh, 24)
			print("Read Nonce:  " + str(nonce))
			os.lseek(fh, offset, os.SEEK_SET)
			plain_chunk = os.read(fh, size)
			cipher = ChaCha20.new(key=self.key, nonce=nonce)
			cipher.seek(offset)
			cipher_chunk = cipher.decrypt(plain_chunk)
			return cipher_chunk

	def readdir(self, path, fh):
		return ['.', '..'] + os.listdir(path)

	readlink = os.readlink

	def release(self, path, fh):
		print("released: " + str(fh))
		return os.close(fh)

	def rename(self, old, new):
		return os.rename(old, self.root + new)

	rmdir = os.rmdir

	def statfs(self, path):
		stv = os.statvfs(path)
		# TODO do any of these need to be modified?
		return dict((key, getattr(stv, key)) for key in (
			'f_bavail', 'f_bfree', 'f_blocks', 'f_bsize', 'f_favail',
			'f_ffree', 'f_files', 'f_flag', 'f_frsize', 'f_namemax'))

	def symlink(self, target, source):
		return os.symlink(source, target)

	def truncate(self, path, length, fh=None):
		with open(path, 'r+b') as f:
			position = f.tell()
			f.seek(-24, os.SEEK_END)
			nonce = f.read(24)
			f.truncate(length)
			f.seek(length, os.SEEK_SET)
			f.write(nonce)
			f.seek(min(length, position))

	unlink = os.unlink
	utimens = os.utime

	def write(self, path, data, offset, fh):
		with self.rwlock:
			nonce = None
			with open(path, "rb") as f:
				f.seek(-24, os.SEEK_END)
				nonce = f.read(24)
				print("Write Nonce: " + str(nonce))
			os.lseek(fh, offset, os.SEEK_SET)
			cipher = ChaCha20.new(key=self.key, nonce=nonce)
			cipher.seek(offset)
			encrypted_chunk = cipher.encrypt(data)
			return os.write(fh, encrypted_chunk)


def open_fuse(root: str, mount: str, key: bytearray) -> fuse.FUSE:
	# throw if realpath of mount is inside root, which creates
	# a recursive subfolder, which messes up directory walking:
	if Path(root) in Path(mount).parents:
		raise Exception("cannot mount the FUSE inside the drive")

	return fuse.FUSE(CrytoOperations(root, key), mount, foreground=True, allow_other=False)


if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('root')
	parser.add_argument('mount')
	args = parser.parse_args()

	logging.basicConfig(level=logging.DEBUG)
	fuse_ = open_fuse(args.root, args.mount)