import os
import nc1

class DSTVProcessor():
	def __init__(self,mark,file,application):
		self.file = file
		self.path = os.path.dirname(file)
		self.application = application
		self.mark = mark

	def getProcesses(self):
		#Checks the config provided by the application for any processes that need to be run on this mark and then returns the list of processes
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
	
	def processDTSV(self,output):
		# get the processes that need to be performed on the part
		processes = self.getProcesses()

		print(f"--- Mark {self.mark["pieceMark"]} ---")

		#check if the mark isn't suppost to be processed
		if "IGNORE" in processes:
			print(f"Performing Process: IGNORE")
		else:
			#check if the file exists before attempting to open it
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

				## Perform processes as defined by process array
				for process in processes:
					print(f"Performing Process: {process}")
					if process == "MARK_DIMENTIONS":
						prepend.append(self.mark["dimension"].replace("/","_"))
				
				for pend in prepend:
					filename = pend + " - " + filename
				for pend in append:
					filename = filename + " - " + pend

				fullPath = os.path.join(directory,subDir,filename)

				markDSTV.writeFile(fullPath)
			else:
				print("No file provided.")