import os
import preprocessor
import bsfile

class TeklaCSV():
	def __init__(self,file,application):
		self.file = file
		self.raw = bsfile.openCSV(file)
		self.application = application
	
	# Combines all pieces that share the same name, adding their quantities
	def getTotals(self):
		totals = {}
		csvConfig = self.application.config["CSV"]
		for row in self.raw:
			rowData = {}
			for col in csvConfig["Headers"]:
				rowData[col] = row[csvConfig["Headers"][col]]
		
			if rowData["pieceMark"] in totals:
				totals[rowData["pieceMark"]]["weight"] = f"{float(totals[rowData["pieceMark"]]["weight"].replace("#","")) + float(rowData["weight"].replace("#",""))}#"
				totals[rowData["pieceMark"]]["quantity"] = int(totals[rowData["pieceMark"]]["quantity"]) + int(rowData["quantity"])
			else:
				totals[rowData["pieceMark"]] = rowData
				totals[rowData["pieceMark"]]["shop"] = "unknown"
		
		return totals
	
	def getTotalWeight(self,shapes=[]):
		totals = self.getTotals();
		weight = 0;
		for part in totals:
			if shapes == []:
				weight += float(totals[part]["weight"].replace("#",""))
			elif totals[part]["shape"] in shapes:
				weight += float(totals[part]["weight"].replace("#",""))
		return weight

	# Combines all pieces under the "parts" property of their respective assemblies
	def getAssemblies(self):
		assemblies = {}
		csvConfig = self.application.config["CSV"]
		for row in self.raw:
			rowData = {}
			for col in csvConfig["Headers"]:
				rowData[col] = row[csvConfig["Headers"][col]]
			if not rowData["mainMark"] in assemblies:
				assemblies[rowData["mainMark"]] = {
					"drawing" : rowData["drawing"],
					"mainMark" : rowData["mainMark"],
					"shop" : "unknown",
					"parts" : {}
				}
			
			assemblies[rowData["mainMark"]]["parts"][rowData["pieceMark"]] = rowData
		
		return assemblies

	def assignShop(self,shop):
		csvConfig = self.application.config["CSV"]
		totals = self.getTotals()
		assemblies = self.getAssemblies()
		
		for assembly in assemblies:
			assemblies[assembly]["shop"] = shop;
			count = 0

			# count all the non ignored items in the assembly
			for part in assemblies[assembly]["parts"]:
				if not assemblies[assembly]["parts"][part]["shape"] in csvConfig["Ignore"]:
					count += 1
			
			if count <= 1:
				if assemblies[assembly]["parts"][assemblies[assembly]["mainMark"]]["shape"] in ["PL","CP"]:
					assemblies[assembly]["shop"] = "stencil & ship"
					
		for part in totals:
			totals[part]["shop"] = assemblies[totals[part]["mainMark"]]["shop"]
		
		return totals


		