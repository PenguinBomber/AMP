import os
import preprocessor
import bsfile

class teklaCSV():
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
            totals[rowData["pieceMark"]] += rowData["quantity"]
        else:
            totals[rowData["pieceMark"]] = rowData
            totals[rowData["pieceMark"]]["shop"] = "unknown"
        
        return totals
    
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
            
            assemblies["parts"][rowData["pieceMark"]] = rowData
        
        return assemblies

    def assignShop(self,shop):
        csvConfig = self.application.config["CSV"]
        totals = self.getTotals()
        assemblies = self.getAssemblies()

        for part in totals:
            if part != totals[part]["mainMark"]:
                totals[part]["shop"] = shop
        
        for assembly in assemblies:
            assemblies[assembly]["shop"] = shop;
            count = 0

            # count all the non ignored items in the assembly
            for part in assemblies[assembly]["parts"]:
                if not part["shape"] in csvConfig["Ignore"]:
                    count += 1
            
            if count <= 1:
                if assemblies["parts"][assemblies["mainMark"]]["shape"] in ["PL","CP"]:
                    assemblies[assembly]["shop"] = "stencil & ship"

        return totals


        