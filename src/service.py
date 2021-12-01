import os
from pathlib import Path
import secrets
from Crypto.Cipher import ChaCha20
import hashlib

import crypter

MACHINE_SECURITY_PATH = Path.home() / ".somedrive"
DRIVE_SECURITY_PATH = ".security"
DRIVE_SECURITY_DRIVE_ID_FILE = "id"
DRIVE_SECURITY_NEW_USER_DOOR_HANDOFF_FILE = "new-user-door-handoff"
DRIVE_SECURITY_DOOR_HANDOFF_FILE = "door-handoff"
DRIVE_SECURITY_DOOR_VAULT_FILE = "door-vault"

DRIVE_ID_SIZE = 32
USER_SECRET_SIZE = 256


class UserId:
	def __init__(self, id: bytearray, email: str, encrypted_drive_key: bytearray):
		self.id = id
		self.email = email
		self.encrypted_drive_key = encrypted_drive_key


class EncryptedDriveService:

	def encrypt_drive(root: str):
		"""
		Throws if drive is already encrypted.
		"""
		drive_id = secrets.token_bytes()
		key = secrets.token_bytes(32)
		user_secret = secrets.token_bytes(USER_SECRET_SIZE)

		crypter.fully_encrypt_drive(root, key)

		# Setup the drive's security folder
		os.makedirs(Path(root, DRIVE_SECURITY_PATH), exist_ok=True)

		# Setup Local Machine's security folder
		os.makedirs(MACHINE_SECURITY_PATH / drive_id.hex(), exist_ok=True)

		# Setup the machine's key file
		with open(MACHINE_SECURITY_PATH / drive_id.hex(), "wb") as user_secret_file:
			user_secret_file.write(user_secret)

		return EncryptedDriveService(drive_root=root, drive_id=drive_id, key=key)


	def get_current_handoff_users(root) -> dict[bytearray, UserId]:
		"""Returns the list of user names in the handoff file."""
		file = Path(root, DRIVE_SECURITY_PATH, DRIVE_SECURITY_DOOR_HANDOFF_FILE)
		user_ids = dict()
		with open(file, "r") as handoff_file:
			for line in handoff_file:
				user_id_hex_str, encrypted_drive_key_hex_str, email = line.split()
				user_id = bytes.fromhex(user_id_hex_str)
				user_ids.update(user_id, UserId(
					user_id,
					None, # Purposely pass `None` to keep it pseudonymous
					bytes.fromhex(encrypted_drive_key_hex_str)
				))
		return user_ids


	def load_encrypted_drive(root: str):
		"""
		Throws if this machine has no user secret for this drive or the user is not in door-handoff.
		"""
		with open(Path(root, DRIVE_SECURITY_PATH, DRIVE_ID_SIZE), "r") as drive_id_file:
			drive_id = bytes.fromhex(drive_id_file.readline())
			with open(MACHINE_SECURITY_PATH / drive_id.hex(), "rb") as user_secret_file:
				user_secret = bytes.fromhex(user_secret_file.readline())
				user_id = hashlib.sha256(user_secret.encode("ascii"))
				cipher = ChaCha20.new(key=user_secret, nonce=bytes(24))
				user = EncryptedDriveService.get_current_handoff_users(root).get(user_id)
				drive_key = cipher.decrypt(user.encrypted_drive_key)
				return EncryptedDriveService(drive_root=root, drive_id=drive_id, key=drive_key)
		pass # TODO


	def is_drive_waiting_for_new_user(root: str):
		"""If true, you can call `load_encrypted_drive__new_user`."""
		return Path(root, DRIVE_SECURITY_PATH, DRIVE_SECURITY_NEW_USER_DOOR_HANDOFF_FILE).is_file()


	def load_encrypted_drive_new_user(root: str, password_input: str, email: str):
		"""
		Do not call this if `is_drive_waiting_for_new_user` returns `False`.
		Returns `None` if password is incorrect.
		"""
		pass_file_name = Path(root, DRIVE_SECURITY_PATH, DRIVE_SECURITY_NEW_USER_DOOR_HANDOFF_FILE)
		with open(pass_file_name, "r") as pass_file:
			pass_hash, encrypted_drive_key_hex_str = pass_file.readline().split()
			pass_hash_input = hashlib.sha256(password_input.encode("ascii")).hexdigest()
			if (pass_hash == pass_hash_input):
				cipher = ChaCha20.new(bytes.fromhex(password_input), nonce=bytes(24))
				drive_key = cipher.decrypt(bytes.fromhex(encrypted_drive_key_hex_str))

				# Securely delete by first overwriting with random bytes
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

				# adds user to door vault
				with open(Path(root, DRIVE_SECURITY_PATH, DRIVE_SECURITY_DOOR_VAULT_FILE), mode="a") as encrypted_door_file:
					cipher = ChaCha20.new(drive_key, nonce=bytes(24))
					cipher.seek(encrypted_door_file.tell())

					# user_id_hex_str encrypted_drive_key_hex_str email
					user_id = hashlib.sha256(user_secret).hexdigest()
					encrypted_door_file.write(cipher.encrypt(user_id + " " + drive_key.hex() + " " + email))

				service = EncryptedDriveService(drive_root=root, drive_id=drive_id, key=drive_key)
				return service
			else:
				return None


	def __init__(self, drive_root: str, drive_id: bytearray, key: bytearray):
		self.drive_root = drive_root
		self.key = key
		self.fuse = None


	def add_new_user(self, temp_password: str):
		""" """
		door_handoff_file_path = Path(self.drive_root, DRIVE_SECURITY_PATH, DRIVE_SECURITY_NEW_USER_DOOR_HANDOFF_FILE)
		with open(door_handoff_file_path, "w") as door_handoff_file:
			temp_password_hash = hashlib.sha256(temp_password.encode("ascii")).hexdigest()
			cipher = ChaCha20.new(temp_password, nonce=bytes(24))
			new_key = cipher.encrypt(self.key.hex())
			door_handoff_file.writeline(temp_password_hash + " " + new_key.encode("ascii"))


	def get_current_vault_users(self) -> list[UserId]:
		"""Returns a list of userIds in the drive vault."""
		file = Path(self.drive_root, DRIVE_SECURITY_PATH, DRIVE_SECURITY_DOOR_VAULT_FILE)
		vault_user_ids = []
		with open(file, "rb") as cipher_vault_file:
			cipher = ChaCha20.new(key=self.key, nonce=bytearray(24))
			plain_vault_file = cipher.decrypt(cipher_vault_file).decode("utf_8")
			for line in plain_vault_file:
				user_id_hex_str, encrypted_drive_key_hex_str, email = line.split()
				vault_user_ids.append(UserId(bytes.fromhex(user_id_hex_str), email))
		return vault_user_ids


	def overwrite_handoff(self, user_ids: list[UserId]):
		"""Append user_id to door handoff file."""
		handoff_file_path = Path(self.drive_root, DRIVE_SECURITY_PATH, DRIVE_SECURITY_DOOR_HANDOFF_FILE)
		with open(handoff_file_path, "w") as handoff_file:
			for user in user_ids:
				handoff_file.write(f"{user.id} {user.encrypted_drive_key} {user.email}")


	def mount_fuse(self, mount_path):
		if self.mount_fuse is not None:
			self.mount_fuse.close() # TODO is this a thing? how do you close it?
		self.mount_fuse = None # TODO
