import os
import nc1
import bsfile

class DSTVProcessor():
	def __init__(self,mark,file,application):
		self.file = file
		self.path = os.path.dirname(file)
		self.application = application
		self.mark = mark

	def getProcesses(self):
		# checks the config provided by the application for any processes that need to be run on this mark and then returns the list of processes
		processes = []
		for shape in self.application.config["Shapes"]:
			if shape == self.mark["shape"]:
				for process in self.application.config["Shapes"][shape]:
					if not process in processes:
						processes.append(process)
		for group in self.application.config["Shape_Groups"]:
			for shape in self.application.config["Shape_Groups"][group]["Shapes"]:
				if shape == self.mark["shape"]:
					for process in self.application.config["Shape_Groups"][group]["Processes"]:
						if not process in processes:
							processes.append(process)
		
		for group in self.application.config["Material_Groups"]:
			for grade in self.application.config["Material_Groups"][group]["Grades"]:
				if grade == self.mark["grade"]:
					for process in self.application.config["Material_Groups"][group]["Processes"]:
						if not process in processes:
							processes.append(process)
		
		return processes
	
	def processDTSV(self,output,job):
		# get the processes that need to be performed on the part
		processes = self.getProcesses()

		print(f"--- Mark {self.mark["pieceMark"]} ---")

		# check if the mark isn't suppost to be processed
		if "IGNORE" in processes:
			print(f"Performing Process: IGNORE")
		else:
			# check if the file exists before attempting to open it
			if self.file != None:
				# check if the function was provided a file location or a directory and act accordingly
				if os.path.isdir(output):
					directory = output
				else:
					directory = os.path.dirname(output)
				filename = self.mark["pieceMark"]
				
				# variables needed by the preprocessor for filename and sub dirs
				subDir = ""
				prepend = []
				append = []
				
				# open the file associated with this object as a DSTV object
				markDSTV = nc1.DSTV(self.file,self.mark["shop"])
				markDSTV.modifyHeader(0,job)
				markDSTV.modifyHeader(1,self.mark["drawing"])
				markDSTV.modifyHeader(2,self.mark["mainMark"])
				markDSTV.modifyHeader(3,self.mark["pieceMark"])
				markDSTV.modifyHeader(5,self.mark["quantity"])

				# perform processes as defined by process array
				for process in processes:
					print(f"Performing Process: {process}")
					if process == "MARK_DIMENTIONS":
						prepend.append(self.mark["dimension"].replace("/","_"))
					if process == "MARK_GRADE":
						append.append(self.mark["grade"].replace("/","_"))
					if process == "NO_HOLES":
						if not "BO" in markDSTV.blocks: 
							append.append("NO HOLES")
					if process == "HOLES":
						if "BO" in markDSTV.blocks: 
							append.append("HOLE")
					if process == "MARK_BENT":
						if "KA" in markDSTV.blocks: 
							append.append("HOLES")
							rolled = False
							bent = False
						
							#bend vs roll checking logic
							for bk in markDSTV.blocks["KA"]:
								if len(bk.split(" ")) == 6:
									if float(bk.split(" ")[5]) > 30:
										rolled = True
									else:
										if abs(float(bk.split(" ")[4])) > 5:
											bent = True
								else:
									if abs(float(bk.split(" ")[4])) > 5:
										bent = True

							if bent:
								append.append("BENT")
							if rolled:
								append.append("ROLLED")
					if process == "SEP_THICKNESS":
						subDir = self.mark["dimension"].split(" x ")[0].replace("/","_")
					if process == "STENCIL_PLATE":
						text = self.mark["shop"][0].capitalize() + job[-3:] + " " + self.mark["pieceMark"]				
						markDSTV.modifyStencil(text)
					if process == "STENCIL_BEAM":
						text = self.mark["shop"][0].capitalize() + job[-3:] + " " + self.mark["pieceMark"]
						if float(markDSTV.getHeader(8).split(",")[0]) > 609.6:
							markDSTV.blocks["SI"] = [f"o 304.8s {float(markDSTV.getHeader(10))-13} 0.00 011 {text}"]

				for pend in prepend:
					filename = pend + " - " + filename
				for pend in append:
					filename = filename + " - " + pend
				bsfile.mkDir(os.path.join(directory,subDir))
				fullPath = os.path.join(directory,subDir,f"{filename}.NC1")

				markDSTV.writeFile(fullPath)
			else:
				print("No file provided.")