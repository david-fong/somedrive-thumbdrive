import os
import pathlib
import psutil
from Crypto.Cipher import ChaCha20
import win32api
import win32con
import win32file
import secrets

# Note: The ChaCha20 stream cipher seems like a sensible choice
# provides efficient random access and has some strengths over AES.

BRAND_FILE_NAME = "thumbprint-thumbdrive.txt"


def get_removable_drives():
    drives = [i for i in win32api.GetLogicalDriveStrings().split('\x00') if i]
    rdrives = [d for d in drives if win32file.GetDriveType(d) == win32con.DRIVE_REMOVABLE]
    return rdrives


def get_encrypted_drives():
    usb_list = get_removable_drives()
    return [x for x in usb_list if is_drive_encrypted(x)]


def get_unenecrypted_drives():
    usb_list = get_removable_drives()
    return [x for x in usb_list if not is_drive_encrypted(x)]


def is_drive_encrypted(root: str) -> bool:
    return pathlib.Path(root, BRAND_FILE_NAME).is_file()


def fully_encrypt_drive(root: str, key: bytearray):
    # throw if the brand file is present
    brand_path = pathlib.Path(root, BRAND_FILE_NAME)

    if brand_path.is_file():
        raise IOError("do not encrypt encrypted drive")

    # walk root and encrypt. skip links.
    for dir, sub_dirs, file_names in os.walk(root):
        for file_name in file_names:
            with open(os.path.join(dir, file_name), mode="r+b") as file:
                print(file.name)

                nonce = secrets.token_bytes(12)     
                cipher = ChaCha20.new(key=key, nonce=nonce)
                while True:
                    write_offset = file.tell()
                    plain_data = file.read(1048576) # 1MB
                    if not plain_data:
                        break
                    cipher_data = cipher.encrypt(plain_data)
                    file.seek(write_offset)
                    file.write(cipher_data)
                    
                file.write(nonce)

    # add the brand file. it contains a hash of the key
    #   Interesting: https://stackoverflow.com/questions/25432139/python-cross-platform-hidden-file
    with open(brand_path, mode="w") as brand_file:
        brand_file.write("") # TODO


def fully_decrypt_drive(root: str, key: bytearray):
    # throw if brand_file is not present
    brand_path = pathlib.Path(root, BRAND_FILE_NAME)
    if not brand_path.is_file():
        raise IOError("do not decrypt unencrypted drive")

    # check that the key hashes to the value in the brand file
    # TODO
    
    # remove the brand file
    os.remove(brand_path)

    # walk root and decrypt. skip links.
    for dir, sub_dirs, file_names in os.walk(root):
        for file_name in file_names:
            with open(os.path.join(dir, file_name), mode="r+b") as file:
                file.seek(-12, os.SEEK_END)
                nonce = file.read(12)
                file.seek(0)               
                
                cipher = ChaCha20.new(key=key, nonce=nonce)
                while True:
                    write_offset = file.tell()
                    cipher_data = file.read(1048576) # 1MB
                    if not cipher_data:
                        break
                    plain_data = cipher.decrypt(cipher_data)
                    file.seek(write_offset)                
                    file.write(plain_data)

                file.seek(-12, os.SEEK_CUR)
                file.truncate(file.tell())
