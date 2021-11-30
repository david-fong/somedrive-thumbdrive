from pathlib import Path
import secrets
from Crypto.Cipher import ChaCha20

MACHINE_SECURITY_PATH = ".tptd/"
DRIVE_SECURITY_PATH = ".security"
DRIVE_SECURITY_NEW_USER_DOOR_HANDOFF_FILE = "new-user-door-handoff"
DRIVE_SECURITY_DOOR_HANDOFF_FILE = "door-handoff"
DRIVE_SECURITY_DOOR_VAULT_FILE = "door-vault"

USER_SECRET_SIZE = 256


class UserId:
    def __init__(self, id: bytearray, email: str, encrypted_drive_key: bytearray):
        self.id = id
        self.email = email
        self.encrypted_drive_key = encrypted_drive_key


class EncryptedDriveService:

    def encrypt_drive(root: str, name: str):
        """
        Throws if drive is already encrypted.
        """
        # TODO
        # Generate Encryption Key
        key = secrets.token_bytes(32)
        # Generate random user secret
        user_secret = secrets.token_bytes(USER_SECRET_SIZE)
        # Encrypt the drive
        # Setup the drive's security folder
        # Setup the machine's key file
        return EncryptedDriveService(root, key)


    def load_encrypted_drive(root: str, name: str):
        """
        Throws if this machine has no user secret for this drive or the user is not in door-handoff.
        """
        # Get secret from machine
        # Use to get key from door_handoff
        pass # TODO


    def is_drive_waiting_for_new_user(root: str):
        """If true, you can call `load_encrypted_drive__new_user`."""
        return Path(root, DRIVE_SECURITY_PATH, DRIVE_SECURITY_NEW_USER_DOOR_HANDOFF_FILE).is_file()


    def load_encrypted_drive_new_user(root: str, name: str, password: str):
        """
        Do not call this if `is_drive_waiting_for_new_user` returns `False`.
        Returns `None` if password is incorrect.
        """
        # If correct, gives them drive key
        # Deletes new_user_door_handoff
        # create user secret file
        # adds user to door vault
        pass # TODO


    def __init__(self, drive_root: str, key: bytearray):
        self.drive_root = drive_root
        self.key = key
        self.fuse = None


    def get_current_handoff_users(self) -> list(UserId):
        """Returns the list of user names in the handoff file."""
        file = Path(self.drive_root, DRIVE_SECURITY_PATH, DRIVE_SECURITY_DOOR_HANDOFF_FILE)
        if file.is_file():
            user_ids = []
            with open(file, "r") as handoff_file:
                for line in handoff_file:
                    user_id_hex_str, encrypted_drive_key_hex_str, email = line.split()
                    user_ids.append(UserId(bytes.fromhex(user_id_hex_str), email))
            return user_ids


    def add_new_user(self, temp_password: str):
        """ """
        # Add user to door vault
        pass # TODO


    def get_current_vault_users(self) -> list(UserId):
        """Returns a list of userIds in the drive vault."""
        file = Path(self.drive_root, DRIVE_SECURITY_PATH, DRIVE_SECURITY_DOOR_VAULT_FILE)
        if file.is_file():
            vault_user_ids = []
            with open(file, "rb") as cipher_vault_file:
                cipher = ChaCha20.new(key=self.key, nonce=bytearray(24))
                plain_vault_file = cipher.decrypt()
                for line in plain_vault_file:
                    user_id_hex_str, encrypted_drive_key_hex_str, email = line.split()
                    vault_user_ids.append(UserId(bytes.fromhex(user_id_hex_str), email))
            return vault_user_ids
        # TODO


    def overwrite_handoff(self, user_ids: list(UserId)):
        """Append user_id to door handoff file."""
        pass # TODO


    def mount_fuse(self, mount_path):
        if self.mount_fuse is not None:
            self.mount_fuse.close() # TODO is this a thing? how do you close it?
        self.mount_fuse = None # TODO
