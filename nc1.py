from colorama import Fore
import re
class DSTV():
	def __init__(self,path,shop=None):
		self.path = path
		self.rawNC1 = []
		self.blocks = {}

		#shop info for auto stenciling
		if (shop == None):
			self.shop = "U"
		else:
			self.shop = shop[0]
		
		#read the file and convert it into a dictionary along with a copy of the original file as a raw list
		with open(self.path) as nc1:
			currentBlock = ""
			for line in nc1:
				#append to the raw list first
				self.rawNC1.append(line)

				#check if we're not at the end of the file
				if currentBlock != "EN":
					#ignore blank lines
					if not line == "\n":
						#ignore comment lines
						if not line.startswith("**"):
							#check if this is the start of a new block
							if not line.startswith("  "):
								#set the current block to the first two letters of the line
								currentBlock = line[:2]
								if not currentBlock in self.blocks:
									self.blocks[currentBlock] = []
							else:
								#append the data to the current block
								self.blocks[currentBlock].append(re.sub(" +", " ",line.strip()))
	
	def getRaw(self):
		out = ""
		for line in self.rawNC1:
			out = out + line
		return out
	
	def getFormated(self):
		out = ""
		for line in self.rawNC1:
			style = ""

			#check if the line is a comment line or a header line and style it appropriately 
			if line.startswith("**"):
				style = Fore.BLUE
			elif not line.startswith("  "):
				style = Fore.GREEN
			
			out = out + style + line + Fore.WHITE
		return out
	
	def getStriped(self):
		out = ""
		for block in self.blocks:
			out = out + block + "\n"
			for line in self.blocks[block]:
				print(line)
				if line != "":
					if line[0] in ["v","u","o","h"]:
						out = out + "  " + line + "\n"
					else:
						out = out + "    " + line + "\n"
				else:
					out = out + "    " + line + "\n"
		return out
	
	def writeFile(self, path):
		#make sure that the end tag is at the end of the file.
		del self.blocks["EN"]
		self.blocks["EN"] = []

		with open(path, "w") as file:
			file.write(self.getStriped())
	
	def getHeader(self, pos):
		return self.blocks["ST"][pos]
	
	def modifyHeader(self, pos, data):
		self.blocks["ST"][pos] = str(data)
	
	def modifyStencil(self,text,x=None,y=None):
		#check for a marking block and add a base one if nothing is found
		if "SI" in self.blocks:
			print("stencil found")
		else:
			self.blocks["SI"] = [f"v 10.00u 10.00 0.00 012 you_should_never_see_this"]

		stencil = self.blocks["SI"][0]
		
		splitStencil = stencil.split(" ")
		
		if x != None:
			splitStencil[1] = f"{x:.1f}s"
			splitStencil[2] = f"{y:.1f}"
		
		#set the text size of the stencil
		splitStencil[4] = "012"
		#set the text of the stencil
		splitStencil[5] = text
		stencil = ""
		for a in splitStencil:
			stencil = stencil + a + " "

		stencil = stencil[:-1]

		self.blocks["SI"][0] = stencil
