import configparser
import json
## Load a default config if the current one is empty
def loadConfig():
	config = {}
	
	try:
		with open("config.json", "r") as configFile:
			config = json.loads(configFile.read())
	except Exception as err:
		config = {}
		print("Failed to load config")
		print(f"Unexpected {err=}, {type(err)=}")
	if config == {}:
		print("Using built in defaults.")
		config = {
			"Main" : {
				"Version" : '1',
				"Use_RFC" : False,
				"RFC_Folder" : r"PLACEHOLDER",
				"debug" : False,
				"useExpermental" : False,
				"MOTD" : "Failed to load config, using built in defaults."
			},
			"CSV" : {
				"Ignore" : ["NU","WA","U-BOLT","MB","HS","","MS"],
				"Headers" : {
					"drawing" : "Dwg",
					"mainMark" : "Main Mk",
					"pieceMark" : "Piece Mk",
					"quantity" : "Qty",
					"batch" : "Lot #",
					"shape" : "Shape",
					"grade" : "Grade",
					"dimension" : "Dimension",
					"weight" : "Gross Weight"
				}
			},
			"Shapes" : {
				"L" : ["MARK_DIMENSIONS"],
				"FB" : ["MARK_DIMENSIONS","MARK_BENT"]
			},
			"Shape_Groups" : {
				"BEAMS" : {
					"Shapes" : ["W","C","S"],
					"Processes" : ["STENCIL_BEAM", "NO_HOLES", "MARK_DIMENSIONS"]
				},
				"PLATES" : {
				"Shapes" : ["PL","CP"],
					"Processes" : ["STENCIL_PLATE", "SEP_THICKNESS", "MARK_BENT"]
					},
				"BOI" : {
					"Shapes" : ["NU","WA","U-BOLT","MB","HS","","MS","SG","STRD"],
					"Processes" : ["IGNORE"]
				}
			},
			"Material_Groups" : {
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
		}
		#with open("config.json", 'w') as configfile:
		#	json.dump(config, configfile,indent=4)
	return config

def loadSection(section):
	return loadConfig()[section]