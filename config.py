import json

config = None

def getTesseractPath() -> str:
	ensureConfigLoaded()
	return config["tesseractPath"]

def ensureConfigLoaded():
	global config
	if config is None:
		with open("config.json", "r") as file:
			config = json.load(file)