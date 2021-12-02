import os
import pathlib
import psutil
import secrets
from Crypto.Cipher import ChaCha20
try:
	import win32api
	import win32con
	import win32file
except:
	pass

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


CHUNK_SIZE = 1048576


def fully_encrypt_drive(root: str, key: bytearray):
	# throw if the brand file is present
	brand_path = pathlib.Path(root, BRAND_FILE_NAME)

	if brand_path.is_file():
		raise IOError("do not encrypt encrypted drive")

	# walk root and encrypt. skip links.
	for dir, sub_dirs, file_names in os.walk(root):
		for file_name in file_names:
			with open(os.path.join(dir, file_name), mode="r+b") as file:
				nonce = secrets.token_bytes(24)
				cipher = ChaCha20.new(key=key, nonce=nonce)
				file.seek(0, os.SEEK_END)
				chunk_end = file.tell()
				file.seek(chunk_end - (chunk_end % CHUNK_SIZE))
				while True:
					pos = file.tell()
					plain_data = file.read(CHUNK_SIZE) # 1MB
					cipher_data = cipher.encrypt(plain_data)
					file.seek(pos+24, os.SEEK_SET)
					file.write(cipher_data)
					if file.tell() >= 24 + 2*CHUNK_SIZE:
						file.seek(-(24 + 2*CHUNK_SIZE), os.SEEK_CUR)
					else:
						break
				file.seek(0, os.SEEK_SET)
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

	# remove the brand file
	os.remove(brand_path)

	# walk root and decrypt. skip links.
	for dir, sub_dirs, file_names in os.walk(root):
		for file_name in file_names:
			with open(os.path.join(dir, file_name), mode="r+b") as file:
				file.seek(0, os.SEEK_END)
				file_size = file.tell()
				file.seek(0, os.SEEK_SET)
				nonce = file.read(24)

				cipher = ChaCha20.new(key=key, nonce=nonce)
				while file.tell() < file_size:
					pos = file.tell()
					cipher_data = file.read(CHUNK_SIZE) # 1MB
					plain_data = cipher.decrypt(cipher_data)
					file.seek(pos-24, os.SEEK_SET)
					file.write(plain_data)
					file.seek(24, os.SEEK_CUR)

				file.seek(-24, os.SEEK_END)
				file.truncate(file.tell())
