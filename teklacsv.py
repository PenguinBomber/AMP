import csv
import shutil
import glob
import nc1
import re
import os
import bsfile

### Shape Catagorys
BeamShapes = ["W","C","S","HSS","WT","MC"]
PlateShapes = ["PL","CP"]
HandrailShapes = ["PIPE"]

### Bought out Item grades + shapes to ignore when pulling NC1 files
BOIShapes = ["NU","WA","U-BOLT","MB","HS","","MS","SG","STRD"]
BOIGrades = ["ZERO_DENSITY"]

### Shapes that will have a suffix added if holes are found in the file
HoleCheck = ["FB"]
### Shapes that will have a suffix added if holes are NOT found in the file
NoHoleCheck = ["C","S","WT","MC","W"]

### Shapes that will have a prefix added for their dimentions
PrefixDimention = ["W","C","S","HSS","WT","MC","L","FB"]

### Outputs a list of all major mark pieces in the CSV, with all associated minor marks in a list per mark, using a table
def getMajors(table):
	mainMarks = {}
	for row in table:
		dwg = row['Dwg']
		mainMark = row['Main Mk']
		piece = row['Piece Mk']
		qty = int(row['Qty'])
		shape = row['Shape']
		if not mainMark in mainMarks:
			mainMarks[mainMark] = {
				"dwg" : dwg,
				"piece" : mainMark,
				"minors" : {}
			}

		if piece != mainMark:
			#filter out bolts
			if not shape in BOIShapes:
				mainMarks[mainMark]["minors"][piece] = {
					"qty" : qty,
					"dwg" : dwg,
					"mainMark" : mainMark,
					"shape" : shape
				}

	return mainMarks

### Outputs a list of pieces marks with quanities from a table
def getTotals(table):
	totals = {}
	for row in table:
		dwg = row['Dwg']
		mainMark = row['Main Mk']
		piece = row['Piece Mk']
		qty = int(row['Qty'])
		seq = row['Lot #']
		shape = row['Shape']
		grade = row['Grade']
		dimension = row['Dimension']
		weight = float(row['Gross Weight'].replace("#",""))

		if piece in totals:
			totals[piece]["qty"] += qty
		else:
			totals[piece] = {
				"qty" : qty,
				"dwg" : dwg,
				"mainMark" : mainMark,
				"seq" : seq,
				"shape" : shape,
				"grade" : grade,
				"shop" : "unknown",
				"dimension" : dimension,
				"weight" : weight
			}
	return totals

### Assigns shops to pieces (needs rework)
def assignShops(table,shop):
	totals = getTotals(table)
	mains = getMajors(table)

	for mark in totals:
		if mark != totals[mark]["mainMark"]:
			totals[mark]["shop"] = shop

	for mark in mains:
		part = mains[mark]

		totals[mark]["shop"] = shop
		if part["minors"] != {}:
			totals[mark]["shop"] = shop
		elif totals[mark]["shape"] in ["PL","CP"]:
			totals[mark]["shop"] = "STENCIL & SHIP"

	return totals

### Pulls the drawing for a given mark, from a given folder
def pullDrawing(lotFolder,outputPath,mark,application):
	dwgPDF = bsfile.searchFiles(lotFolder,f"*{mark["dwg"]}*.pdf")
	#Drawing Pulling logic
	#check if the drawing exists
	if dwgPDF == None:
		application.log(f"DRAWING {mark["dwg"]} NOT FOUND!!")
	else:
		#create the dwg folder
		bsfile.mkDir(f"{outputPath}\\dwgs")
			
		#create the shop folder
		bsfile.mkDir(f"{outputPath}\\dwgs\\{mark["shop"]}")
		
		#copy the dwgs
		shutil.copy(dwgPDF,f"{outputPath}\\dwgs\\{mark["shop"]}\\")
		shutil.copy(dwgPDF,f"{outputPath}\\dwgs\\")

### Pulls all required NC1 files, pre-processes them, grabs drawings, and puts them all into one folder using a CSV produced from the Production Control page of Tekla EPM
def pullFiles(CSVPath,outputPath,job,majorityShop,application):
	table = bsfile.openCSV(CSVPath)
	allClear = True
	totals = assignShops(table,majorityShop)
	beamTonnage = 0
	tonnage = 0
	partCount = 0
	for mark in totals:
		problem = False
		RFCFolder = r"PLACEHOLDER"
		lotFolder = f"{RFCFolder}\\*{job}*{totals[mark]["seq"]}*"
		file = bsfile.searchFiles(lotFolder,f"{mark}.nc1")
		
		#set the save folder for the nc1 file
		subFolder = totals[mark]["shape"]
				
		#make sure the path exists
		bsfile.mkDir(f"{outputPath}\\{subFolder}")
		
		pullDrawing(lotFolder,outputPath,totals[mark],application)
		application.log(f"> Pulling files for {mark} on lot {totals[mark]["seq"]}")
		if not totals[mark]["shape"] in BOIShapes and not totals[mark]["grade"] in BOIGrades:
			#add weights
			tonnage += totals[mark]["weight"]
			if totals[mark]["mainMark"] == mark:
				partCount += totals[mark]["qty"]
			
			#check if the part is a pipe as they use diffent files
			
			if totals[mark]["shape"] in HandrailShapes:
				#STP File Logic
				#only pull mainMark handrails
				if totals[mark]["mainMark"] == mark:
					file = bsfile.searchFiles(lotFolder,f"*{mark}*.stp")
					if file == None:
						application.log(f"{mark}.stp NOT FOUND! Skipping....")
						problem = True
					else:
						shutil.copy(file,f"{outputPath}\\{subFolder}\\{mark}.stp")
			else:
				#NC1 File Logic
				if file == None:
					application.log(f"{mark}.nc1 NOT FOUND! Skipping....")
					problem = True
				else:
					#open the DSTV File found for the part
					markDSTV = nc1.DSTV(file,majorityShop)
					
					#create the thickness folders for plate and checkered plate
					if totals[mark]["shape"] in PlateShapes:
						thickness = totals[mark]["dimension"].split(" x ")[0].replace("/","_")
						print(thickness)
						subFolder = subFolder + "\\" + thickness
						bsfile.mkDir(f"{outputPath}\\{subFolder}")
					
					#variable for appending to the filename for bend and shop marking
					append = ""
					prepend = ""
					
					if totals[mark]["shape"] in HoleCheck:
						if "BO" in markDSTV.blocks:
							append = append + " - HOLES"

					if totals[mark]["shape"] in NoHoleCheck:
						if not "BO" in markDSTV.blocks:
							append = append + " - NO HOLES"
							
							
					if totals[mark]["shape"] in PrefixDimention:
						prepend = totals[mark]["dimension"].replace("/","_") + " - " + prepend
					
					#check for a bent block
					if "KA" in markDSTV.blocks:
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
						
						#logging for bends
						if bent:
							application.log(f"{mark} has bend: dwg {totals[mark]["dwg"]}")
							append = append + " - BENT"
						if rolled:
							application.log(f"{mark} has roll: dwg {totals[mark]["dwg"]}")
							append = append + " - ROLLED"
						
						#write to bends.csv in the same folder as the nc1 file
						if os.path.isfile(f"{outputPath}\\{subFolder}\\bends.csv"):
							mode = "a"
						else:
							mode = "w"
						
						with open(f"{outputPath}\\{subFolder}\\bends.csv", mode) as bendFile:
							bendFile.write(f"{mark},{totals[mark]["dwg"]}\n")
					
					#check if the stencil is different from the majority, log if different
					if totals[mark]["shop"][0].capitalize() != majorityShop[0].capitalize():
						application.log(f"{mark} is not majority: {totals[mark]["shop"]}")
						append = append + f" - {totals[mark]["shop"]}"
					
					#set the header info
					markDSTV.modifyHeader(0,job)
					markDSTV.modifyHeader(1,totals[mark]["dwg"])
					markDSTV.modifyHeader(2,totals[mark]["mainMark"])
					markDSTV.modifyHeader(3,mark)
					markDSTV.modifyHeader(5,totals[mark]["qty"])
					
					#write the new stencil and write the modified nc1 file to the correct folder
					
					#shape checking and stencil writing
					if totals[mark]["shape"] in BeamShapes:
						print(f"Beam Weight: {beamTonnage/2000}")
						beamTonnage = beamTonnage + totals[mark]["weight"]
						#check if the beam is longer then 2 foot
						if float(markDSTV.getHeader(8).split(",")[0]) > 609.6:
							text = totals[mark]["shop"][0].capitalize() + job[-3:] + " " + mark
							markDSTV.blocks["SI"] = [f"o 304.8s {float(markDSTV.getHeader(10))-13} 0.00 011 {text}"]
						else:
							markDSTV.blocks["SI"] = []
					elif totals[mark]["shape"] in PlateShapes:
						markDSTV.modifyStencil(totals[mark]["shop"][0].capitalize() + job[-3:] + " " + mark)
					
					#write file to working folder
					del markDSTV.blocks["EN"]
					markDSTV.blocks["EN"] = []
					markDSTV.writeFile(f"{outputPath}\\{subFolder}\\{prepend + mark + append}.nc1" )
		else:
			application.log(f"{mark} is BOI")
		if problem:
			application.log(f"!!! Issues detected with {mark}, see above !!!")
			allClear = False
		else:
			application.log(f"No detected issues with {mark}")
	application.log("\n--- Final Totals ---")
	
	if tonnage < 2000:
		application.log(f"Tonnage: under 1 ton")
	else:
		application.log(f"Tonnage: {round(tonnage/2000)} tons")
	
	application.log(f"Piece Count: {partCount}")
	
	if beamTonnage == 0:
		application.log(f"Beam Tonnage: 0 tons")
	elif beamTonnage < 2000:
		application.log(f"Beam Tonnage: under 1 ton")
	else:
		application.log(f"Beam Tonnage: {round(beamTonnage/2000)} tons")
		
	if allClear == False:
		application.log("! Issues detected, see above log !")
