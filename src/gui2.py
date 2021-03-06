import tkinter
from tkinter import ttk
from tkinter import *
from ttkbootstrap import Style
from PIL import ImageTk,Image
from pathlib import Path
import service

mode = "ENCRYPT"
IMAGE_MAIN = "usb-icon5.png"
IMAGE_ICON = "usb-icon8.png"
IMAGE_FOLDER = "images"
# TODO:
#   -> Create skeleton pages for each interaction (main page, thumbprint scan pop up window)
#   -> Populate drop down menus for encrypted drives to open or decrypt, non-encrypted drives to encrypt -> david n brandon will get me a list of these
#   -> Maybe? Have an option at first for what you'd like to do?
#   ->> ie. first page asks if you want to: open encrypted drive, decrypt encrypted drive, encrypt non-encrypted drive
#       so then the first page is more clear?

class Application(tkinter.Tk):

	def __init__(self):
		super().__init__()
		self.style = Style('journal')
		self.title('SOMEdrive Thumbdrive')
		self.window = mainWindow()
		self.wm_geometry("400x150")
		self.resizable(0,0)
		photo = ImageTk.PhotoImage(Image.open(Path(IMAGE_FOLDER, IMAGE_ICON)))
		self.iconphoto(False, photo)
		self.window.pack(side='top', fill='both', expand='yes')

class Page(ttk.Frame):
	def __init__(self, *args, **kwargs):
		ttk.Frame.__init__(self, *args, **kwargs)
	def show(self):
		self.lift()

#class fingerPrintScan(Page):
#    def __init__(self):
#        super().__init__()
#        label = ttk.Label(self, text = "To verify your identity, please scan your thumb on the finger scanner")
#        label.pack(side="top", fill="both", expand=True)

class optionSelection(Page):
	def __init__(self):
		Page.__init__(self)
		label = ttk.Label(self, text = "options")
		label.pack(side="top", fill = "both", expand=True)

class driveSelection(Page):
	def __init__(self):
		Page.__init__(self)

		self.columnconfigure(0, weight=1)
		self.columnconfigure(0, weight=1)
		self.driveTextVar = StringVar()
		self.driveTextVar.set("Please select which drive you would like to " + mode.lower())

		label = Label(self, textvariable = self.driveTextVar)
		label.grid(column=0, row=0, sticky=tkinter.W+tkinter.E, pady=6, padx=6, columnspan=2)
		#label.place(relx=.5, rely=.4)

		drives = ["drive1", "drive2", "drive3"] #we would replace this with the function call

		self.driveVar = StringVar()
		self.driveVar.set(drives[0])

		dropdown = OptionMenu(self, self.driveVar, *drives)
		dropdown.grid(column=0, row=1, sticky=tkinter.W+tkinter.E, pady=6, padx=6, columnspan=2)
		#dropdown.place(relx=.5, rely=0.5)

		self.confirmButton = ttk.Button(self, text = mode, command = lambda:[self.thumbscanWindow()])
		self.confirmButton.grid(column=0, row=2, sticky=tkinter.W+tkinter.E, pady=3, padx=6)

		#self.backButton = ttk.Button(self, text = "Back", command = lambda:[parentWindow.goToOs()])
		# self.backButton.grid(column=1, row=2, sticky=tkinter.W+tkinter.E, pady=3, padx=6)
		#self.confirmButton.place(relx=.5, rely=0.6, anchor="c")

	def thumbscan(self):
		#label = ttk.Label(self, text = "main page skeleton")
		#label.pack(side="top", fill="both", expand=True)
		print(self.driveVar.get())
		#open thumbscan window

	def thumbscanWindow(self):
		tsWindow = Toplevel()
		tsLabel = ttk.Label(tsWindow, text = "Please scan your thumbprint on your finger scanner")
		tsButton = ttk.Button(tsWindow, text = "Scan", command = lambda:[self.executeThumbScan(tsWindow)])
		self.confirmButton["state"] = "disabled"
		tsWindow.wm_geometry("400x400")

		tsLabel.place(relx=.5, rely=0.5, anchor="c")
		tsButton.place(relx=.5, rely=0.6, anchor="c")

	def executeThumbScan(self, tsWindow):
		#thumbscan stuff
		tsWindow.destroy()
		self.confirmButton["state"] = "enabled"

class manageUsers(Page):
	def __init__(self):
		Page.__init__(self)
		self.columnconfigure(0, weight=1)

		drives = ["drive1", "drive2", "drive3"] #we would replace this with the function call

		self.driveVar = StringVar()
		self.driveVar.set(drives[0])

		dropdown = OptionMenu(self, self.driveVar, *drives)
		dropdown.grid(column=0, row=0, sticky=tkinter.W+tkinter.E, pady=6, padx=6)
		#dropdown.place(relx=.5, rely=0.5)

		self.newUserButton = ttk.Button(self, text = "Add New User to Drive", command = lambda:[self.newUserWindow()])
		self.newUserButton.grid(column=0, row=1, sticky=tkinter.W+tkinter.E, pady=3, padx=6)

		self.handoffUserButton = ttk.Button(self, text = "Handoff to Specific User", command = lambda:[self.handoffUserWindow()])
		self.handoffUserButton.grid(column=0, row=2, sticky=tkinter.W+tkinter.E, pady=3, padx=6)

	def newUserWindow(self):
		nuWindow = Toplevel()
		tsLabel = ttk.Label(nuWindow, text = "New User")
		tsButton = ttk.Button(nuWindow, text = "Confirm", command = lambda:[nuWindow.destroy()])
		self.newUserButton["state"] = "disabled"
		self.handoffUserButton["state"] = "disabled"
		nuWindow.wm_geometry("400x400")

		tsLabel.place(relx=.5, rely=0.5, anchor="c")
		tsButton.place(relx=.5, rely=0.6, anchor="c")

	def handoffUserWindow(self):
		hoWindow = Toplevel()
		tsLabel = ttk.Label(hoWindow, text = "Handoff User")
		tsButton = ttk.Button(hoWindow, text = "Confirm", command = lambda:[hoWindow.destroy()])
		self.newUserButton["state"] = "disabled"
		self.handoffUserButton["state"] = "disabled"
		hoWindow.wm_geometry("400x400")

		tsLabel.place(relx=.5, rely=0.5, anchor="c")
		tsButton.place(relx=.5, rely=0.6, anchor="c")

class mainWindow(ttk.Frame):
	def __init__(self):
		ttk.Frame.__init__(self)

		self.ds = driveSelection()
		self.mu = manageUsers()

		buttonFrame = ttk.Frame(self)
		container = ttk.Frame(self)

		container.columnconfigure(0, weight=3)
		container.columnconfigure(0, weight=1)
		container.pack(side="top", fill="both", expand=True)
		buttonFrame.pack(side="bottom", expand=False)

		img = ImageTk.PhotoImage(Image.open(Path(IMAGE_FOLDER, IMAGE_MAIN)).resize((256, 128), Image.ANTIALIAS))

		self.imageLabel = ttk.Label(container, image = img)
		self.imageLabel.image = img
		self.imageLabel.grid(column=0, row=0, sticky=tkinter.N+tkinter.S, rowspan=4, padx=6)

		self.encryptButton = ttk.Button(container, text = "Encrypt", command = lambda:[self.ds.place(in_=container, x=0, y=0, width=400, relheight=1), self.goToDS("ENCRYPT")])
		self.openButton = ttk.Button(container, text = "Open", command = lambda:[self.ds.place(in_=container, x=0, y=0, width=400, relheight=1), self.goToDS("OPEN")])
		self.decryptButton = ttk.Button(container, text = "Decrypt", command = lambda:[self.ds.place(in_=container, x=0, width=400, y=0, relheight=1), self.goToDS("DECRYPT")])
		self.manageUserButton = ttk.Button(container, text = "Manage Users", command = lambda:[self.mu.place(in_=container, x=0, width=400, y=0, relheight=1), self.goToDS("DECRYPT")])

		self.encryptButton.grid(column=1, row=0, sticky=tkinter.W+tkinter.E, pady=3, padx=6)
		self.openButton.grid(column=1, row=1, sticky=tkinter.W+tkinter.E, pady=3, padx=6)
		self.decryptButton.grid(column=1, row=2, sticky=tkinter.W+tkinter.E, pady=3, padx=6)
		self.manageUserButton.grid(column=1, row=3, sticky=tkinter.W+tkinter.E, pady=3, padx=6)

		self.backButton = ttk.Button(self.ds, text = "Back", command = lambda:[self.ds.place_forget(), self.goToOs()])
		self.backFromUsers = ttk.Button(self.mu, text = "Back", command = lambda:[self.mu.place_forget(), self.goToOsFromMu()])


	# have function for each button to switch pages
	# place the buttons instead of packing
	# can have button for each option?? and each option can pass in a certain argument to get the correct list, one function for the option
	def goToDS(self, modeArg):
		mode = modeArg
		print(mode)
		self.encryptButton.grid_forget()
		self.openButton.grid_forget()
		self.decryptButton.grid_forget()
		self.imageLabel.grid_forget()
		self.manageUserButton.grid_forget()
		self.ds.confirmButton.configure(text=mode)
		self.ds.confirmButton.grid(column=0, row=2, sticky=tkinter.W+tkinter.E, pady=3, padx=6)
		self.ds.driveTextVar.set("Please select which drive you would like to " + mode.lower())
		#self.label.pack_forget()

		self.backButton.grid(column=1, row=2, sticky=tkinter.W+tkinter.E, pady=3, padx=6)
		self.backFromUsers.grid(column=0, row=3, sticky=tkinter.W+tkinter.E, pady=3, padx=6)
		#self.ds.confirmButton.pack(side = "top", pady = "6")
		#self.ds.show()

	def goToOs(self):
		self.ds.confirmButton.pack_forget()
		self.ds.grid_forget()
		self.backButton.grid_forget()
		#self.label.place(relx=.5, rely=0.3, anchor="c")
		self.encryptButton.grid(column=1, row=0, sticky=tkinter.W+tkinter.E, pady=3, padx=6)
		self.openButton.grid(column=1, row=1, sticky=tkinter.W+tkinter.E, pady=3, padx=6)
		self.decryptButton.grid(column=1, row=2, sticky=tkinter.W+tkinter.E, pady=3, padx=6)
		self.imageLabel.grid(column=0, row=0, sticky=tkinter.N+tkinter.S, rowspan=4, padx=6)
		self.manageUserButton.grid(column=1, row=3, sticky=tkinter.W+tkinter.E, pady=3, padx=6)

	def goToOsFromMu(self):
		self.mu.grid_forget()
		self.backFromUsers.grid_forget()
		#self.label.place(relx=.5, rely=0.3, anchor="c")
		self.encryptButton.grid(column=1, row=0, sticky=tkinter.W+tkinter.E, pady=3, padx=6)
		self.openButton.grid(column=1, row=1, sticky=tkinter.W+tkinter.E, pady=3, padx=6)
		self.decryptButton.grid(column=1, row=2, sticky=tkinter.W+tkinter.E, pady=3, padx=6)
		self.imageLabel.grid(column=0, row=0, sticky=tkinter.N+tkinter.S, rowspan=4, padx=6)
		self.manageUserButton.grid(column=1, row=3, sticky=tkinter.W+tkinter.E, pady=3, padx=6)




if __name__ == '__main__':
	Application().mainloop()