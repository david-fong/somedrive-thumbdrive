import os
from pathlib import Path
import shutil
import secrets
from Crypto.Cipher import ChaCha20
import hashlib
try:
	import win32api
	import win32con
	import win32file
except:
	pass

import crypter
import fusehandler

MACHINE_SECURITY_PATH = Path.home() / ".somedrive"
DRIVE_SECURITY_PATH = ".security"
DRIVE_SECURITY_DRIVE_ID_FILE = "id"
DRIVE_SECURITY_NEW_USER_DOOR_HANDOFF_FILE = "new-user-door-handoff"
DRIVE_SECURITY_DOOR_HANDOFF_FILE = "door-handoff"
DRIVE_SECURITY_DOOR_VAULT_FILE = "door-vault"

DRIVE_ID_SIZE = 32
USER_SECRET_SIZE = 32


class UserId:
	def __init__(self, id: bytes, email: str, encrypted_drive_key: bytes):
		self.id = id
		self.email = email
		self.encrypted_drive_key = encrypted_drive_key


def get_removable_drives():
	drives = [i for i in win32api.GetLogicalDriveStrings().split('\x00') if i]
	rdrives = [d for d in drives if win32file.GetDriveType(d) == win32con.DRIVE_REMOVABLE]
	return rdrives


def get_encrypted_drives():
	usb_list = get_removable_drives()
	return [x for x in usb_list if is_drive_encrypted(x)]


def get_unencrypted_drives():
	usb_list = get_removable_drives()
	return [x for x in usb_list if not is_drive_encrypted(x)]


def is_drive_encrypted(root: str):# -> bool:
	return Path(root, DRIVE_SECURITY_PATH).is_dir()


class EncryptedDriveService:

	def encrypt_drive(root: str, user_email: str):
		"""
		Throws if drive is already encrypted.
		"""
		drive_id = secrets.token_bytes()
		key = secrets.token_bytes(32)
		user_secret = secrets.token_bytes(USER_SECRET_SIZE)

		# throw if the security folder is present
		security_folder = Path(root, DRIVE_SECURITY_PATH)
		if Path(root, DRIVE_SECURITY_PATH).is_dir():
			raise IOError("do not encrypt encrypted drive")

		crypter.fully_encrypt_drive(root, key)

		# Setup the drive's security folder
		os.makedirs(security_folder, exist_ok=True)
		with open(security_folder / DRIVE_SECURITY_DRIVE_ID_FILE, "wb") as f:
			f.write(drive_id)
		with open(security_folder / DRIVE_SECURITY_DOOR_HANDOFF_FILE, "w") as handoff, open(security_folder / DRIVE_SECURITY_DOOR_VAULT_FILE, "wb") as vault:
			user_id = hashlib.sha256(user_secret).hexdigest()
			key_cipher = ChaCha20.new(key=user_secret, nonce=bytes(24))
			encrypted_drive_key_hex_str = key_cipher.encrypt(key).hex()
			handoff.write(f"{user_id} {encrypted_drive_key_hex_str}\n")
			vault_cipher = ChaCha20.new(key=key, nonce=bytes(24))
			vault.write(vault_cipher.encrypt(f"{user_id} {encrypted_drive_key_hex_str} {user_email}\n".encode("ascii")))

		# Setup Local Machine's security folder
		os.makedirs(MACHINE_SECURITY_PATH, exist_ok=True)
		with open(MACHINE_SECURITY_PATH / drive_id.hex(), "wb") as user_secret_file:
			user_secret_file.write(user_secret)

		return EncryptedDriveService(drive_root=root, drive_id=drive_id, key=key)


	def get_current_handoff_users(root):# -> dict[bytes, UserId]:
		"""Returns the list of user names in the handoff file."""
		file = Path(root, DRIVE_SECURITY_PATH, DRIVE_SECURITY_DOOR_HANDOFF_FILE)
		user_ids = dict()
		with open(file, "r") as handoff_file:
			for line in handoff_file:
				if len(line) == 0:
					continue
				user_id_hex_str, encrypted_drive_key_hex_str = line.split()
				user_id = bytes.fromhex(user_id_hex_str)
				user_ids[user_id] = UserId(
					user_id,
					None, # Purposely pass `None` to keep it pseudonymous
					bytes.fromhex(encrypted_drive_key_hex_str)
				)
		return user_ids


	def load_encrypted_drive(root: str):
		"""
		Throws if this machine has no user secret for this drive or the user is not in door-handoff.
		"""
		with open(Path(root, DRIVE_SECURITY_PATH, DRIVE_SECURITY_DRIVE_ID_FILE), "rb") as drive_id_file:
			drive_id = drive_id_file.read(DRIVE_ID_SIZE)
			with open(MACHINE_SECURITY_PATH / drive_id.hex(), "rb") as user_secret_file:
				user_secret = user_secret_file.read(USER_SECRET_SIZE)
				user_id = hashlib.sha256(user_secret).digest()
				cipher = ChaCha20.new(key=user_secret, nonce=bytes(24))
				user = EncryptedDriveService.get_current_handoff_users(root).get(user_id)
				if user == None:
					raise PermissionError("user is not in door handoff")
				drive_key = cipher.decrypt(user.encrypted_drive_key)
				return EncryptedDriveService(drive_root=root, drive_id=drive_id, key=drive_key)


	def is_drive_waiting_for_new_user(root: str):
		"""If true, you can call `load_encrypted_drive__new_user`."""
		return Path(root, DRIVE_SECURITY_PATH, DRIVE_SECURITY_NEW_USER_DOOR_HANDOFF_FILE).is_file()


	def load_encrypted_drive_new_user(root: str, password_input: str, user_email: str):
		"""
		Do not call this if `is_drive_waiting_for_new_user` returns `False`.
		Returns `None` if password is incorrect.
		"""
		pass_file_name = Path(root, DRIVE_SECURITY_PATH, DRIVE_SECURITY_NEW_USER_DOOR_HANDOFF_FILE)
		with open(pass_file_name, "r") as pass_file:
			pass_key_hash_hex_str, encrypted_drive_key_hex_str = pass_file.readline().split()
			pass_in_key = hashlib.sha256(password_input.encode("ascii")).digest()
			pass_in_key_hash_hex_str = hashlib.sha256(pass_in_key).hexdigest()
			if (pass_key_hash_hex_str == pass_in_key_hash_hex_str):
				cipher = ChaCha20.new(key=pass_in_key, nonce=bytes(24))
				drive_key = cipher.decrypt(bytes.fromhex(encrypted_drive_key_hex_str))
			else:
				return None # Securely delete by first overwriting with random bytes

		with open(pass_file_name, "ab") as pass_file:
			pass_file.seek(0, os.SEEK_END)
			pass_file_size = pass_file.tell()
			pass_file.seek(0, os.SEEK_SET)
			pass_file.write(secrets.token_bytes(pass_file_size))
		os.remove(pass_file_name)

		# create user secret file
		user_secret = secrets.token_bytes(USER_SECRET_SIZE)
		with open(Path(root, DRIVE_SECURITY_PATH, DRIVE_SECURITY_DRIVE_ID_FILE), "rb") as drive_id_file:
			drive_id = drive_id_file.read(DRIVE_ID_SIZE)
			os.makedirs(MACHINE_SECURITY_PATH, exist_ok=True)
			with open(MACHINE_SECURITY_PATH / drive_id.hex(), "wb") as user_secret_file:
				user_secret_file.write(user_secret)

		# add user to door vault
		with open(Path(root, DRIVE_SECURITY_PATH, DRIVE_SECURITY_DOOR_VAULT_FILE), mode="ab") as door_vault_file:
			drive_key_cipher = ChaCha20.new(key=user_secret, nonce=bytes(24))
			encrypted_drive_key = drive_key_cipher.encrypt(drive_key)
			cipher = ChaCha20.new(key=drive_key, nonce=bytes(24))
			cipher.seek(door_vault_file.tell())
			user_id_hex_str = hashlib.sha256(user_secret).hexdigest()
			door_vault_file.write(cipher.encrypt(f"{user_id_hex_str} {encrypted_drive_key.hex()} {user_email}\n".encode("ascii")))

		# add user to door handoff
		with open(Path(root, DRIVE_SECURITY_PATH, DRIVE_SECURITY_DOOR_HANDOFF_FILE), mode="a") as handoff_file:
			# user_id_hex_str encrypted_drive_key_hex_str
			handoff_file.write(f"{user_id_hex_str} {encrypted_drive_key.hex()}\n")

		service = EncryptedDriveService(drive_root=root, drive_id=drive_id, key=drive_key)
		return service


	def __init__(self, drive_root: str, drive_id: bytes, key: bytes):
		self.drive_root = drive_root
		self.drive_id = drive_id
		self.key = key
		self.fuse = None


	def decrypt_drive(self):
		# throw if the security folder is not present
		if not Path(self.drive_root, DRIVE_SECURITY_PATH).is_dir():
			raise IOError("do not decrypt unencrypted drive")

		shutil.rmtree(Path(self.drive_root, DRIVE_SECURITY_PATH))
		crypter.fully_decrypt_drive(root=self.drive_root, key=self.key)
		os.remove(MACHINE_SECURITY_PATH / self.drive_id.hex())


	def add_new_user(self, temp_password: str):
		""" """
		door_handoff_file_path = Path(self.drive_root, DRIVE_SECURITY_PATH, DRIVE_SECURITY_NEW_USER_DOOR_HANDOFF_FILE)
		with open(door_handoff_file_path, "w") as door_handoff_file:
			pass_key = hashlib.sha256(temp_password.encode("ascii")).digest()
			pass_key_hash = hashlib.sha256(pass_key).hexdigest()
			cipher = ChaCha20.new(key=pass_key, nonce=bytes(24))
			encrypted_drive_key = cipher.encrypt(self.key).hex()
			door_handoff_file.write(f"{pass_key_hash} {encrypted_drive_key}")


	def get_current_vault_users(self):# -> list[UserId]:
		"""Returns a list of userIds in the drive vault."""
		file = Path(self.drive_root, DRIVE_SECURITY_PATH, DRIVE_SECURITY_DOOR_VAULT_FILE)
		vault_user_ids = {}
		with open(file, "rb") as cipher_vault_file:
			cipher = ChaCha20.new(key=self.key, nonce=bytes(24))
			plain_vault_file = cipher.decrypt(cipher_vault_file.read()).decode("ascii")
			for line in plain_vault_file.split("\n"):
				if len(line) == 0:
					continue
				user_id_hex_str, encrypted_drive_key_hex_str, email = line.split()
				vault_user_ids[email] = UserId(
					bytes.fromhex(user_id_hex_str),
					email,
					bytes.fromhex(encrypted_drive_key_hex_str)
				)
		return vault_user_ids


	def overwrite_handoff(self, user_ids):
		"""Append user_id to door handoff file."""
		handoff_file_path = Path(self.drive_root, DRIVE_SECURITY_PATH, DRIVE_SECURITY_DOOR_HANDOFF_FILE)
		with open(handoff_file_path, "w") as handoff_file:
			for user in user_ids:
				handoff_file.write(f"{user.id.hex()} {user.encrypted_drive_key.hex()}\n")


	def mount_fuse(self, mount_path):
		# if self.mount_fuse is not None:
		# 	self.mount_fuse.close() # TODO is this a thing? how do you close it?
		self.mount_fuse = fusehandler.open_fuse(root=self.drive_root, mount=mount_path, key=self.key)


if __name__ == '__main__':
	s = EncryptedDriveService.encrypt_drive("test-dir", "davidfong19@gmail.com")
	input("press a key to continue.")