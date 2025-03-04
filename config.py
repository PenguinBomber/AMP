import configparser

## Load a default config if the current one is empty
def loadConfig():
	config = configparser.ConfigParser()
	config.read("config.ini")
	if config.sections() == []:
		config['Main'] = {
			"Version" : '1',
			"Use_RFC" : True,
			"RFC_Folder" : r"\\10.10.1.106\Public\File Transfer\RFC Packages",
			"debug" : False
		}
		config['Shapes'] = {
			"L" : ["MARK_DIMENTIONS"],
			"FB" : ["MARK_DIMENTIONS","MARK_BENT"]
		}
		config["Shape_Groups"] = {
			"BEAMS" : {
				"Shapes" : ["W","C","S"],
				"Processes" : ["STENCIL", "NO_HOLES", "MARK_DIMENTIONS"]
			},
			"PLATES" : {
				"Shapes" : ["PL","CP"],
				"Processes" : ["STENCIL", "SEP_THICKNESS", "MARK_BENT"]
			},
			"BOI" : {
				"Shapes" : ["NU","WA","U-BOLT","MB","HS","","MS","SG","STRD"],
				"Processes" : ["IGNORE"]
			}
		}
		config["Material_Groups"] = {
			"BOI" : {
				"Grades" : ["ZERO_DENSITY"],
				"Processes" : ["IGNORE"]
			},
			"STAINLESS" : {
				"Grades" : ["316L"],
				"Processes" : ["MARK_GRADE"]
			},
			"ALUMINUM" : {
				"Grades" : ["316L"],
				"Processes" : ["MARK_GRADE"]
			}
		}
		with open("config.ini", 'w') as configfile:
			config.write(configfile)
	return config

def loadSection(section):
	return loadConfig()[section]

print(loadSection("Material_Groups")["BOI"]["Grades"])