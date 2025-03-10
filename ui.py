import tkinter.ttk
import tkinter.scrolledtext
import teklacsv
from tkinter.constants import *
from tkinter import filedialog as fd

class Application(tkinter.ttk.Frame):

	@classmethod
	def main(cls):
		tkinter.NoDefaultRoot()
		root = tkinter.Tk()
		root.title("AMP")
		app = cls(root)
		app.grid(sticky=NSEW)
		root.grid_columnconfigure(0, weight=0)
		root.grid_columnconfigure(1, weight=1)
		root.grid_rowconfigure(0, weight=1)
		root.resizable(False, False)
		root.mainloop()

	def __init__(self, root):
		super().__init__(root)
		self.create_variables()
		self.create_widgets()
		self.grid_widgets()
		self.grid_columnconfigure(0, weight=1)

	def create_variables(self):
		self.csvPath = ''
		self.outPath = ''

		self.csvPathDisplay = tkinter.StringVar(self, 'Select File')
		self.outPathDisplay = tkinter.StringVar(self, 'Select Folder')

		self.jobVar = tkinter.StringVar(self, '')
		self.shopVar = tkinter.StringVar(self, '')

	def create_widgets(self):
		options = dict(sticky=NSEW, padx=3, pady=4)
		self.createInputFrame(options)
		self.textOut = tkinter.scrolledtext.ScrolledText(self,state='disabled')

	def createInputFrame(self,options):
		self.inputFrame = tkinter.Frame(self)

		#create the entry boxs
		self.csvPathEntry = tkinter.ttk.Button(self.inputFrame, textvariable=self.csvPathDisplay,command=self.csvPressed, width=15)
		self.outPathEntry = tkinter.ttk.Button(self.inputFrame, textvariable=self.outPathDisplay,command=self.outPathPressed, width=15)
		self.jobEntry = tkinter.ttk.Entry(self.inputFrame, textvariable=self.jobVar, width=15)
		self.shopEntry = tkinter.ttk.Entry(self.inputFrame, textvariable=self.shopVar, width=15)

		self.startButton = tkinter.ttk.Button(self.inputFrame, text='Start', command=self.startPressed)


		#create the labels for the entry boxes
		self.versionLabel = tkinter.ttk.Label(self.inputFrame, text="Version 0.96")
		self.csvPathLabel = tkinter.ttk.Label(self.inputFrame, text="CSV File")
		self.outPathLabel = tkinter.ttk.Label(self.inputFrame, text="Output Folder")
		self.jobLabel = tkinter.ttk.Label(self.inputFrame, text="Job Number")
		self.shopLabel = tkinter.ttk.Label(self.inputFrame, text="Shop")
		self.copyrightLabel = tkinter.ttk.Label(self.inputFrame, text="Copyright © 2025, Bryce Schuman")

		#place all of the widgets into the input grid
		self.versionLabel.grid(column=0, row=0, columnspan=2, **options)
		self.csvPathEntry.grid(column=1, row=1, **options)
		self.csvPathLabel.grid(column=0, row=1, **options)
		self.outPathEntry.grid(column=1, row=2, **options)
		self.outPathLabel.grid(column=0, row=2, **options)
		self.jobEntry.grid(column=1, row=3, **options)
		self.jobLabel.grid(column=0, row=3, **options)
		self.shopEntry.grid(column=1, row=4, **options)
		self.shopLabel.grid(column=0, row=4, **options)
		self.startButton.grid(column=0, row=5, columnspan=2, **options)
		self.copyrightLabel.grid(column=0, row=6, columnspan=2, **options)


	def grid_widgets(self):
		options = dict(sticky=NSEW, padx=3, pady=4)
		self.inputFrame.grid(column=0, row=0, **options)
		self.textOut.grid(column=1, row=0, **options)

	def log(self,info):
		self.textOut.config(state='normal')
		self.textOut.insert(END, info + "\n")
		self.textOut.config(state='disabled')

	def csvPressed(self):
		path = fd.askopenfilename(
            title="Select CSV File",
            filetypes=(
                ("CSV Files", r"*.csv"),
                ("All Files", r"*.*")
            ),
			parent=self
		)
		self.csvPathDisplay.set(path[-15:])
		self.csvPath = path

	def outPathPressed(self):
		path = fd.askdirectory(parent=self)
		self.outPathDisplay.set(path[-15:])
		self.outPath = path

	def startPressed(self):
		#self.log(self.csvPath)
		#self.log(self.outPath)
		self.log(f"Job Number: {self.jobVar.get()}")
		self.log(f"Shop: {self.shopVar.get()}")
		try:
			teklacsv.pullFiles(self.csvPath,self.outPath, self.jobVar.get(), self.shopVar.get(),self)
		except Exception as err:
			self.log(f"Unexpected {err=}, {type(err)=}")
		self.log("\nPart pull complete.")
