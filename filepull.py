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
        
    def pullDrawings(self):
        data = teklaCSV2.TeklaCSV(self.csv,self.application)
        totals = data.assignShop(self.shop)
        
        for part in totals:
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
                shutil.copy(drawingPath,drawingFolder)
                #make the shop folder and copy the drawing into it
                bsfile.mkDir(os.path.join(drawingFolder,totals[part]["shop"]))
                shutil.copy(drawingPath,os.path.join(drawingFolder,totals[part]["shop"]))
    
    def pullCNC(self):
        data = teklaCSV2.TeklaCSV(self.csv,self.application)
        totals = data.assignShop(self.shop)
        
        for part in totals:
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
                    file = shutil.copy(cncPath,cncFolder)
                    name = os.path.basename(file)
                    
                    processor = preprocessor.DSTVProcessor(totals[part],file,self.application)
                    processor.processDTSV(os.path.join(processedFolder,name),self.job)