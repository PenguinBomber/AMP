import configparser
import json
## Load a default config if the current one is empty
def loadConfig():
	config = {}
	
	try:
		with open("config.json", "r") as configFile:
			config = json.loads(configFile.read())
	except:
		config = {}
	if config == {}:
		config = {
			"Main" : {
				"Version" : '1',
				"Use_RFC" : False,
				"RFC_Folder" : r"PLACEHOLDER",
				"debug" : False
			},
			"Shapes" : {
				"L" : ["MARK_DIMENTIONS"],
				"FB" : ["MARK_DIMENTIONS","MARK_BENT"]
			},
			"Shape_Groups" : {
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
		with open("config.json", 'w') as configfile:
			json.dump(config, configfile,indent=4)
	return config

def loadSection(section):
	return loadConfig()[section]