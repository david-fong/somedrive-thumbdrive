import tkinter
from tkinter import ttk
from tkinter import *
from ttkbootstrap import Style

mode = "ENCRYPT"
# TODO: 
#   -> Create skeleton pages for each interaction (main page, thumbprint scan pop up window)
#   -> Populate drop down menus for encrypted drives to open or decrypt, non-encrypted drives to encrypt -> david n brandon will get me a list of these
#   -> Maybe? Have an option at first for what you'd like to do? 
#   ->> ie. first page asks if you want to: open encrypted drive, decrypt encrypted drive, encrypt non-encrypted drive
#       so then the first page is more clear?
#   open -> text box for path to open

class Application(tkinter.Tk):

    def __init__(self):
        super().__init__()
        self.style = Style('journal')
        self.title('Thumbprint Thumbdrive')
        self.window = mainWindow()
        self.wm_geometry("400x400")
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

        self.driveTextVar = StringVar()
        self.driveTextVar.set("Please select which drive you would like to " + mode.lower())

        label = Label(self, textvariable = self.driveTextVar)
        label.place(relx=.5, rely=.4, anchor="c")

        drives = ["drive1", "drive2", "drive3"] #we would replace this with the function call

        self.driveVar = StringVar()
        self.driveVar.set(drives[0])

        dropdown = OptionMenu(self, self.driveVar, *drives)
        dropdown.place(relx=.5, rely=0.5, anchor="c")

        self.confirmButton = ttk.Button(self, text = mode, command = lambda:[self.thumbscan(), self.thumbscanWindow()])
        self.confirmButton.place(relx=.5, rely=0.6, anchor="c")

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




class mainWindow(ttk.Frame):
    def __init__(self):
        ttk.Frame.__init__(self)
        
        self.ds = driveSelection()
        #options = optionSelection()

        buttonFrame = ttk.Frame(self)
        container = ttk.Frame(self)
        
        container.pack(side="top", fill="both", expand=True)
        buttonFrame.pack(side="bottom", expand=False)

        #fps.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        #options.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        self.label = ttk.Label(container, text = "Welcome to thumbprint thumbdrive")
        self.label.place(relx=.5, rely=0.3, anchor="c")

        self.encryptButton = ttk.Button(container, text = "Encrypt", command = lambda:[self.ds.place(in_=container, x=0, y=0, relwidth=1, relheight=1), self.goToDS("ENCRYPT")])
        self.openButton = ttk.Button(container, text = "Open", command = lambda:[self.ds.place(in_=container, x=0, y=0, relwidth=1, relheight=1), self.goToDS("OPEN")])
        self.decryptButton = ttk.Button(container, text = "Decrypt", command = lambda:[self.ds.place(in_=container, x=0, y=0, relwidth=1, relheight=1), self.goToDS("DECRYPT")])

        self.encryptButton.place(relx=.5, rely=0.4, anchor="c")
        self.openButton.place(relx=.5, rely=0.5, anchor="c")
        self.decryptButton.place(relx=.5, rely=0.6, anchor="c")

        self.backButton = ttk.Button(buttonFrame, text = "Back", command = lambda:[self.ds.place_forget(), self.goToOs()])
        
        #bFPS.pack(side="left")
        #self.ds.place_forget()
        
    
    # have function for each button to switch pages
    # place the buttons instead of packing
    # can have button for each option?? and each option can pass in a certain argument to get the correct list, one function for the option
    def goToDS(self, modeArg):
        mode = modeArg
        print(mode)
        self.encryptButton.pack_forget()
        self.openButton.pack_forget()
        self.decryptButton.pack_forget()
        self.ds.confirmButton.configure(text=mode)
        self.ds.driveTextVar.set("Please select which drive you would like to " + mode.lower())
        #self.label.pack_forget()
        
        self.backButton.pack(side = "bottom", pady = "6")
        #self.ds.confirmButton.pack(side = "top", pady = "6")
        #self.ds.show()

    def goToOs(self):
        self.ds.confirmButton.pack_forget()
        self.backButton.pack_forget()
        self.label.place(relx=.5, rely=0.3, anchor="c")
        self.encryptButton.place(relx=.5, rely=0.4, anchor="c")
        self.openButton.place(relx=.5, rely=0.5, anchor="c")
        self.decryptButton.place(relx=.5, rely=0.6, anchor="c")



if __name__ == '__main__':
    Application().mainloop()