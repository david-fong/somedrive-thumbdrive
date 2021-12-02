import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QInputDialog, QMessageBox
from pathlib import Path

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
        #prompt for email TODO
        #encryptDrive TODO
        changeWindow(MAIN_WINDOW)

    def setup(self):
        #get unencrypted drives TODO
        listOfDrives = ["Drive 1", "Drive 2"]
        self.unencryptedBox.clear()
        self.unencryptedBox.addItems(listOfDrives)
        if (not self.unencryptedBox.currentText()):
            self.encryptConfirm.setEnabled(False)
        else:
            self.encryptConfirm.setEnabled(True)


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
            self.openConfirm.setEnabled(False)
            self.buttonEnroll.setEnabled(False)
            self.buttonHandoff.setEnabled(False)
            self.buttonFullDe.setEnabled(False)

        self.buttonDeCancel.clicked.connect(self.cancel)
        self.buttonEnroll.clicked.connect(self.enroll)
        self.buttonHandoff.clicked.connect(self.handoff)
        self.openConfirm.clicked.connect(self.openUSB)
        self.buttonFullDe.clicked.connect(self.fullDecrypt)

    def cancel(self):
        changeWindow(MAIN_WINDOW)
        self.setWindowTitle("Main")

    def enroll(self):
        #changeWindow(PASSWORD_WINDOW)
        self.getTempPassword()

    def getTempPassword(self):
        text, ok = QInputDialog.getText(self, 'Text Input Dialog', 'Enter your temporary password:')
        if ok:
            print(text)
            self.showErrorMessage()

        else:
            self.showErrorMessage()

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

    def openUSB(self):
        #Check if user has permission TODO
        #Prompt for password if no permission TODO
        #Give popup saying password status TODO
        #Redirect to decrypt or home TODO
        #TODO
        pass

    def fullDecrypt(self):
        #Check if user has permission TODO
        #Prompt for password if no permission TODO
        #Give popup saying password status TODO
        #Redirect to decrypt or home TODO
        pass

    def setup(self):
        #Get drives here
        #TODO
        listOfDrives = ["Drive 1", "Drive 2"]
        self.driveBox.clear()
        self.driveBox.addItems(listOfDrives)
        if (not self.driveBox.currentText()):
            self.openConfirm.setEnabled(False)
            self.buttonEnroll.setEnabled(False)
            self.buttonHandoff.setEnabled(False)
            self.buttonFullDe.setEnabled(False)
        else:
            self.openConfirm.setEnabled(True)
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

    def cancel(self):
        changeWindow(DECRYPT_WINDOW)
        self.textUsers.clear()

    def addUserToBox(self):
        userToAdd = self.emailBox.currentText()
        self.textUsers.append(userToAdd)
        self.handoffConfirm.setEnabled(True)

    def getEmails(self):
        emails = self.textUsers.toPlainText()
        changeWindow(MAIN_WINDOW)
        print(emails)
        #Add users to handoff TODO
        #Send back to homescreen TODO
        self.textUsers.clear()

    def setup(self):
        #Get User Emails from Vault
        #TODO
        listOfEmails = ["mslongo@live.ca", "email2", "email3"]
        self.emailBox.clear()
        self.emailBox.addItems(listOfEmails)
        if (not self.emailBox.currentText()):
            self.buttonAdd.setEnabled(False)
        else:
            self.buttonAdd.setEnabled(True)
        self.handoffConfirm.setEnabled(False)
        self.textUsers.clear()


def changeWindow(newWindow):
    if (newWindow[0] == INDEX_DE):
        decrypt.setup()
    elif (newWindow[0] == INDEX_HAND):
        handoff.setup()
    elif (newWindow[0] == INDEX_EN):
        encrypt.setup()
    widget.setCurrentIndex(newWindow[0])
    widget.resize(newWindow[1], newWindow[2])


app = QApplication(sys.argv)
widget = QtWidgets.QStackedWidget(objectName="SOMEprintSomedrive")
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