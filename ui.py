import tkinter.ttk
import tkinter.scrolledtext
import filepull
from tkinter.constants import *
from tkinter import filedialog as fd

class Application(tkinter.ttk.Frame):

	@classmethod
	def main(self,config):
		self.config = config
		tkinter.NoDefaultRoot()
		root = tkinter.Tk()
		root.title("AMP")
		app = self(root)
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
		self.log(f"AMP Started.")
		if "MOTD" in self.config["Main"]:
			self.log(self.config["Main"]["MOTD"])

	def create_variables(self):
		self.csvPath = ''
		self.outPath = ''
		if self.config["Main"]["Use_RFC"]:
			self.inPath = self.config["Main"]["RFC_Folder"]
		else:
			self.inPath = ''

		self.csvPathDisplay = tkinter.StringVar(self, 'Select File')
		self.outPathDisplay = tkinter.StringVar(self, 'Select Folder')
		self.inPathDisplay = tkinter.StringVar(self, 'Select Folder')

		self.jobVar = tkinter.StringVar(self, '')
		self.shopVar = tkinter.StringVar(self, '')

	def create_widgets(self):
		options = dict(sticky=NSEW, padx=3, pady=4)
		self.createInputFrame(options)
		self.textOut = tkinter.scrolledtext.ScrolledText(self,state='disabled')

	def createInputFrame(self,options):
		self.inputFrame = tkinter.Frame(self)

		#create the entry boxs
		self.inPathEntry = tkinter.ttk.Button(self.inputFrame, textvariable=self.inPathDisplay,command=self.inPathPressed, width=15)
		self.csvPathEntry = tkinter.ttk.Button(self.inputFrame, textvariable=self.csvPathDisplay,command=self.csvPressed, width=15)
		self.outPathEntry = tkinter.ttk.Button(self.inputFrame, textvariable=self.outPathDisplay,command=self.outPathPressed, width=15)
		self.jobEntry = tkinter.ttk.Entry(self.inputFrame, textvariable=self.jobVar, width=15)
		self.shopEntry = tkinter.ttk.Entry(self.inputFrame, textvariable=self.shopVar, width=15)

		self.startButton = tkinter.ttk.Button(self.inputFrame, text='Start', command=self.startPressed)


		#create the labels for the entry boxes
		self.versionLabel = tkinter.ttk.Label(self.inputFrame, text="Version 1.0")
		self.inPathLabel = tkinter.ttk.Label(self.inputFrame, text="Input Folder")
		self.csvPathLabel = tkinter.ttk.Label(self.inputFrame, text="CSV File")
		self.outPathLabel = tkinter.ttk.Label(self.inputFrame, text="Output Folder")
		self.jobLabel = tkinter.ttk.Label(self.inputFrame, text="Job Number")
		self.shopLabel = tkinter.ttk.Label(self.inputFrame, text="Shop")
		self.copyrightLabel = tkinter.ttk.Label(self.inputFrame, text="Copyright © 2025, Bryce Schuman")

		#place all of the widgets into the input grid
		row = 0
		self.versionLabel.grid(column=0, row=row, columnspan=2, **options)
		row += 1
		if self.config["Main"]["Use_RFC"] == False:
			self.inPathEntry.grid(column=1, row=row, **options)
			self.inPathLabel.grid(column=0, row=row, **options)
			row += 1
		self.csvPathEntry.grid(column=1, row=row, **options)
		self.csvPathLabel.grid(column=0, row=row, **options)
		row += 1
		self.outPathEntry.grid(column=1, row=row, **options)
		self.outPathLabel.grid(column=0, row=row, **options)
		row += 1
		self.jobEntry.grid(column=1, row=row, **options)
		self.jobLabel.grid(column=0, row=row, **options)
		row += 1
		self.shopEntry.grid(column=1, row=row, **options)
		self.shopLabel.grid(column=0, row=row, **options)
		row += 1
		self.startButton.grid(column=0, row=row, columnspan=2, **options)
		row += 1
		self.copyrightLabel.grid(column=0, row=row, columnspan=2, **options)
		row += 1



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
	
	def inPathPressed(self):
		path = fd.askdirectory(parent=self)
		self.inPathDisplay.set(path[-15:])
		self.inPath = path

	def startPressed(self):
		#self.log(self.csvPath)
		#self.log(self.outPath)
		self.log(f"Job Number: {self.jobVar.get()}")
		self.log(f"Shop: {self.shopVar.get()}")
		if self.config["Main"]["debug"]:
			run = filepull.FilePull(self.csvPath,self.inPath,self.outPath,self.jobVar.get(), self.shopVar.get(),self)
			run.pullDrawings()
			run.pullCNC()
			run.pullTonnage()
		else:
			try:
				run = filepull.FilePull(self.csvPath,self.inPath,self.outPath,self.jobVar.get(), self.shopVar.get(),self)
				run.pullDrawings()
				run.pullCNC()
				run.pullTonnage()
				self.log("\nPart pull complete.")
			except Exception as err:
				self.log(f"Unexpected {err=}, {type(err)=}")
				self.log("\nPart pull failed.")

