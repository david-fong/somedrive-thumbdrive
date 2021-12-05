import sys
from typing import Text
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QInputDialog, QMessageBox, QLineEdit, QFileDialog
from pathlib import Path
import service

INDEX_MAIN = 0
INDEX_EN = 1
INDEX_DE = 2
INDEX_PASS = 3
INDEX_HAND = 4
INDEX_EMAIL = 5

MAIN_WINDOW = [INDEX_MAIN, 440, 50]
ENCRYPT_WINDOW = [INDEX_EN, 310, 90]
DECRYPT_WINDOW = [INDEX_DE, 440, 87]
PASSWORD_WINDOW = [INDEX_PASS, 305, 90]
HANDOFF_WINDOW = [INDEX_HAND, 400, 310]
EMAIL_WINDOW = [INDEX_EMAIL, 305, 90]

MAIN_PATH = Path("ui", "MainWindow.ui")
ENCRYPT_PATH = Path("ui", "Encrypt.ui")
DECRYPT_PATH = Path("ui", "Decrypt.ui")
HANDOFF_PATH = Path("ui", "Handoff.ui")
PASS_PATH = Path("ui", "ConfirmPassword.ui")

class MainWindow(QDialog):
	def __init__(self):
		super(MainWindow, self).__init__()
		loadUi(MAIN_PATH, self)
		self.buttonEncrypt.clicked.connect(self.goToEncrypt)
		self.buttonDecrypt.clicked.connect(self.goToDecrypt)

	def goToEncrypt(self):
		changeWindow(ENCRYPT_WINDOW)
		self.setWindowTitle("Encryption")

	def goToDecrypt(self):
		changeWindow(DECRYPT_WINDOW)
		self.setWindowTitle("Decryption")


class Encrypt(QDialog):
	def __init__(self):
		super(Encrypt, self).__init__()
		loadUi(ENCRYPT_PATH, self)
		self.buttonEnCancel.clicked.connect(self.cancel)
		self.encryptConfirm.clicked.connect(self.encryption)

	def cancel(self):
		changeWindow(MAIN_WINDOW)
		self.setWindowTitle("Main")

	def encryption(self):
		drivename = self.unencryptedBox.currentText()
		email, ok = self.getEmail()
		if ok:
			if email:
				service.encrypt_drive(drivename, email)
				changeWindow(MAIN_WINDOW)

	def setup(self):
		listOfDrives = service.get_unencrypted_drives()
		self.unencryptedBox.clear()
		self.unencryptedBox.addItems(listOfDrives)
		if (not self.unencryptedBox.currentText()):
			self.encryptConfirm.setEnabled(False)
		else:
			self.encryptConfirm.setEnabled(True)

	def getEmail(self):
		text, ok = QInputDialog.getText(self, 'Text Input Dialog', 'Enter your email for handoffs:')
		return (text, ok)


class ConfirmPass(QDialog):
	def __init__(self):
		super(ConfirmPass, self).__init__()
		loadUi(PASS_PATH, self)
		self.buttonUserCancel.clicked.connect(self.cancel)

	def cancel(self):
		changeWindow(DECRYPT_WINDOW)


class Decrypt(QDialog):
	def __init__(self):
		super(Decrypt, self).__init__()
		loadUi(DECRYPT_PATH, self)
		if (not self.driveBox.currentText()):
			self.mountConfirm.setEnabled(False)
			self.buttonEnroll.setEnabled(False)
			self.buttonHandoff.setEnabled(False)
			self.buttonFullDe.setEnabled(False)

		self.buttonDeCancel.clicked.connect(self.cancel)
		self.buttonEnroll.clicked.connect(self.enroll)
		self.buttonHandoff.clicked.connect(self.handoff)
		self.mountConfirm.clicked.connect(self.mountUSB)
		self.buttonFullDe.clicked.connect(self.fullDecrypt)
		self.driveBox.activated.connect(self.authenticate)
		self.driveInstance = None
		self.mountPath = ""

	def cancel(self):
		changeWindow(MAIN_WINDOW)
		self.setWindowTitle("Main")

	def enroll(self):
		tempPassword, ok = self.getTempPassword('Enter temporary password for new user:')
		if ok:
			print(tempPassword)
			if (self.driveInstance and self.driveInstance != 1):
				self.driveInstance.add_new_user(tempPassword)
				self.buttonEnroll.setEnabled(False)
			else:
				print("No Drive Instance")

	def getTempPassword(self, stringPrompt):
		text, ok = QInputDialog.getText(self, 'Temporary Password', stringPrompt, QLineEdit.Password)
		return (text, ok)

	def getEmail(self, stringPrompt):
		text, ok = QInputDialog.getText(self, 'Email', stringPrompt)
		return (text, ok)

	def showErrorMessage(self):
		msgBox = QMessageBox()
		msgBox.setIcon(QMessageBox.Warning)
		msgBox.setText("An Unknown Error Occurred")
		msgBox.setWindowTitle("Password Error")
		msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
		msgBox.buttonClicked.connect(Decrypt.msgButtonClick)
		returnValue = msgBox.exec()
		changeWindow(MAIN_WINDOW)

	def msgButtonClick(i):
		print("Button was clicked")

	def handoff(self):
		changeWindow(HANDOFF_WINDOW)

	def mountUSB(self):
		if (self.mountConfirm.text() == "Mount..."):
			self.mountPath = self.promptForFilepath()
			if (self.driveInstance and self.driveInstance != 1):
				self.driveInstance.mount_fuse(self.mountPath)

			self.mountConfirm.setText("Unmount")
		else:
			self.driveInstance.unmount_fuse()
			self.mountConfirm.setText("Mount...")


	def fullDecrypt(self):
		self.driveInstance.decrypt_drive()
		changeWindow(MAIN_WINDOW)

	def promptForFilepath(self):
		fname = str(QFileDialog.getExistingDirectory(self, "Location to Mount", str(Path.home())))
		return fname

	def authenticate(self):
		currentDrive = self.driveBox.currentText()
		try:
			self.driveInstance = service.load_encrypted_drive(currentDrive)
		except Exception as err:
			print(err)
			password, passOk = self.getTempPassword('Enter your temporary password:')
			if (passOk):
				email, emailOk = self.getEmail("Enter email this machine with:")
				if (emailOk):
					try:
						self.driveInstance = service.load_encrypted_drive_new_user(currentDrive, password, email)
					except:
						print("Would get drive here")
						self.driveInstance = 1

		if (self.driveInstance == None):
			self.mountConfirm.setEnabled(False)
			self.buttonEnroll.setEnabled(False)
			self.buttonHandoff.setEnabled(False)
			self.buttonFullDe.setEnabled(False)
		else:
			self.mountConfirm.setEnabled(True)
			self.buttonEnroll.setEnabled(True)
			self.buttonHandoff.setEnabled(True)
			self.buttonFullDe.setEnabled(True)


	def setup(self):
		listOfDrives = service.get_encrypted_drives()
		listOfDrives.insert(0, "")
		self.driveBox.clear()
		self.driveBox.addItems(listOfDrives)
		if (not self.driveBox.currentText()):
			self.mountConfirm.setEnabled(False)
			self.buttonEnroll.setEnabled(False)
			self.buttonHandoff.setEnabled(False)
			self.buttonFullDe.setEnabled(False)
		else:
			self.mountConfirm.setEnabled(True)
			self.buttonEnroll.setEnabled(True)
			self.buttonHandoff.setEnabled(True)
			self.buttonFullDe.setEnabled(True)


class Handoff(QDialog):
	def __init__(self):
		super(Handoff, self).__init__()
		loadUi(HANDOFF_PATH, self)
		self.buttonHandoffCancel.clicked.connect(self.cancel)
		self.buttonAdd.clicked.connect(self.addUserToBox)
		self.handoffConfirm.clicked.connect(self.getEmails)
		self.listOfIdObjects = None

	def cancel(self):
		self.listOfIdObjects = None
		changeWindow(DECRYPT_WINDOW, INDEX_HAND)
		self.textUsers.clear()

	def addUserToBox(self):
		userToAdd = self.emailBox.currentText()
		self.textUsers.append(userToAdd)
		self.handoffConfirm.setEnabled(True)

	def getEmails(self):
		emails = set(self.textUsers.toPlainText().split("\n"))
		listOfEmails = [email.strip() for email in emails]
		objectIdList = []
		for email in listOfEmails:
			objectIdList.append(self.listOfIdObjects[email])
		decrypt.driveInstance.overwrite_handoff(objectIdList)
		print(listOfEmails)
		self.listOfIdObjects = None
		changeWindow(DECRYPT_WINDOW, INDEX_HAND)

		# Send back to homescreen TODO
		self.textUsers.clear()

	def setup(self):
		self.listOfIdObjects = decrypt.driveInstance.get_current_vault_users()
		listOfEmails = self.listOfIdObjects.keys()
		self.emailBox.clear()
		self.emailBox.addItems(listOfEmails)
		if (not self.emailBox.currentText()):
			self.buttonAdd.setEnabled(False)
		else:
			self.buttonAdd.setEnabled(True)
		self.handoffConfirm.setEnabled(False)
		self.textUsers.clear()


def changeWindow(newWindow, currentIndex=0):
	if (newWindow[0] == INDEX_DE and currentIndex != INDEX_HAND):
		decrypt.setup()
	elif (newWindow[0] == INDEX_HAND):
		handoff.setup()
	elif (newWindow[0] == INDEX_EN):
		encrypt.setup()
	widget.setCurrentIndex(newWindow[0])
	widget.resize(newWindow[1], newWindow[2])


app = QApplication(sys.argv)
widget = QtWidgets.QStackedWidget(objectName="SOMEprintThumbdrive")
mainWindow = MainWindow()
encrypt = Encrypt()
decrypt = Decrypt()
confirmPass = ConfirmPass()
handoff = Handoff()


widget.addWidget(mainWindow)
widget.addWidget(encrypt)
widget.addWidget(decrypt)
widget.addWidget(confirmPass)
widget.addWidget(handoff)
widget.show()

try:
	sys.exit(app.exec_())
except:
	print("Bye")