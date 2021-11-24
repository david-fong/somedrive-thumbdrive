import tkinter
from tkinter import ttk
from ttkbootstrap import Style

mode = "ENCRYPT"
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
        label = ttk.Label(self, text = "main page skeleton")
        label.pack(side="top", fill="both", expand=True)

class mainWindow(ttk.Frame):
    def __init__(self):
        ttk.Frame.__init__(self)
        
        ds = driveSelection()
        options = optionSelection()

        buttonFrame = ttk.Frame(self)
        container = ttk.Frame(self)
        buttonFrame.pack(side="top", fill="x", expand=False)
        container.pack(side="top", fill="both", expand=True)

        #fps.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        options.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        ds.place(in_=container, x=0, y=0, relwidth=1, relheight=1)

        self.encryptButton = ttk.Button(buttonFrame, text = "Encrypt", command = lambda:[ds.show(), self.goToDS("ENCRYPT")])
        self.openButton = ttk.Button(buttonFrame, text = "Open", command = lambda:[ds.show(), self.goToDS("OPEN")])
        self.decryptButton = ttk.Button(buttonFrame, text = "Decrypt", command = lambda:[ds.show(), self.goToDS("DECRYPT")])

        self.encryptButton.pack(side="top")
        self.openButton.pack(side="top")
        self.decryptButton.pack(side="top")
        
        #bFPS.pack(side="left")
        options.show()
        
    
    # have function for each button to switch pages
    # place the buttons instead of packing
    # can have button for each option?? and each option can pass in a certain argument to get the correct list, one function for the option
    def goToDS(self, modeArg):
        mode = modeArg
        self.encryptButton.pack_forget()
        self.openButton.pack_forget()
        self.decryptButton.pack_forget()
        #self.ds.show()



if __name__ == '__main__':
    Application().mainloop()