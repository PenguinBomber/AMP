import preprocessor
import teklaCSV2
import bsfile
import os
import shutil

class FilePull():
	def __init__(self,csv,inputFolder,outputFolder,job,shop,application):
		self.inputFolder = inputFolder
		self.outputFolder = outputFolder
		self.shop = shop
		self.job = job
		self.application = application
		self.csv = csv
	
	def pullTonnage(self):
		data = teklaCSV2.TeklaCSV(self.csv,self.application)
		totalWeight = data.getTotalWeight()
		totalAss = data.getAssemblyCount()
		totalBeamWeight = data.getTotalWeight(["W","HSS","C","S"])

		if totalWeight < 2000:
			if totalWeight == 0:
				displayTonnage = "0 Tons"
			else:
				displayTonnage = "Under 1 Ton"
		else:
			displayTonnage = f"{round(totalWeight/2000)} ton(s)"
		
		if totalBeamWeight < 2000:
			if totalBeamWeight == 0:
				displayBeamTonnage = "0 Tons"
			else:
				displayBeamTonnage = "Under 1 Ton"
		else:
			displayBeamTonnage = f"{round(totalBeamWeight/2000)} ton(s)"
		
		self.application.log(f"Beam Tonnage: {displayBeamTonnage}")
		self.application.log(f"Assembly Count: {totalAss}")
		self.application.log(f"Tonnage: {displayTonnage}")

	def pullDrawings(self):
		threads = []
		data = teklaCSV2.TeklaCSV(self.csv,self.application)
		totals = data.assignShop(self.shop)
		
		self.application.log("Starting Drawing Pull...")
		for part in totals:
			self.application.log(f"Pulling Drawings for {part}")

			if self.application.config["Main"]["Use_RFC"]:
				query = f"*{self.job}*{totals[part]['batch']}*"
				sourceFolder = os.path.join(self.inputFolder,"**",query)
			else:
				sourceFolder = self.inputFolder
				
			drawingPath = bsfile.searchFiles(sourceFolder,f"*{totals[part]['drawing']}*.pdf")
			print(sourceFolder)
			if drawingPath != None:
				print("pulling")
				drawingFolder = os.path.join(self.outputFolder,"Drawings")
				bsfile.mkDir(drawingFolder)
				#copy into the main drawing folder
				threads.append(bsfile.asyncCopy(drawingPath,drawingFolder))
				#make the shop folder and copy the drawing into it
				bsfile.mkDir(os.path.join(drawingFolder,totals[part]["shop"]))
				threads.append(bsfile.asyncCopy(drawingPath,os.path.join(drawingFolder,totals[part]["shop"])))
				self.application.log(f"Drawing found for {part} - {os.path.basename(drawingPath)}")
			else:
				self.application.log(f"No Drawing found for {part}!")
			
			self.application.log("")
		bsfile.threadClean(threads)
			
	def pullCNC(self):
		threads = []
		data = teklaCSV2.TeklaCSV(self.csv,self.application)
		totals = data.assignShop(self.shop)
		
		self.application.log("Starting CNC Pull...")
		for part in totals:
			self.application.log(f"Pulling CNC for {part}")
			if not totals[part]['shape'] in self.application.config["CSV"]["Ignore"]:
				if self.application.config["Main"]["Use_RFC"]:
					query = f"*{self.job}*{totals[part]['batch']}*"
					sourceFolder = os.path.join(self.inputFolder,"**",query)
				else:
					sourceFolder = self.inputFolder
					
				cncPath = bsfile.searchFiles(sourceFolder,f"*{totals[part]['pieceMark']}*.nc1")
				
				print(sourceFolder)
				if cncPath != None:
					print("pulling")
					cncFolder = os.path.join(self.outputFolder,"CNC",f"{totals[part]['shape']}")
					processedFolder = os.path.join(self.outputFolder,"Processed CNC",f"{totals[part]['shape']}")

					bsfile.mkDir(cncFolder)
					#copy into the main drawing folder
					threads.append(bsfile.asyncCopy(cncPath,cncFolder))
					self.application.log(f"CNC found for {part} - {os.path.basename(cncPath)}")

					processor = preprocessor.DSTVProcessor(totals[part],cncPath,self.shop,self.application)
					threads.append(processor.asyncProcessDTSV(os.path.join(processedFolder,os.path.basename(cncPath)),self.job))
					self.application.log(f"CNC processed for {part}")
				else:
					self.application.log(f"No CNC found for {part}!")
			
			self.application.log("")
		bsfile.threadClean(threads)
