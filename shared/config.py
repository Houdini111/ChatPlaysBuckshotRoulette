import json
import logging
import os
from typing import TypeVar
from typing_extensions import TypeAlias

logging.getLogger(__name__)

T = TypeVar("T")

class Config():
	def __init__(self):
		self.loadConfig()
	
	def loadConfig(self) -> None:
		with open("config.json", "r", encoding="utf-16") as file:
			self.innerDict = json.load(file)
	
	def getKeyOrDefault(self, key: str, expectedType: type, defaultValue: T) -> T:
		val = self.getKey(key, expectedType)
		if val is None:
			return defaultValue
		else:
			return val

	def getKey(self, key: str, expectedType: type) -> T | None:
		val = self.innerDict.get(key)
		if val is None:
			return None
		if type(val) is expectedType:
			return val
		return expectedType(val)

config: Config = Config()

def getTesseractPath() -> str:
	return config.getKeyOrDefault("tesseractPath", str, r"C:\Program Files\Tesseract-OCR\tesseract")

def getChannels() -> list[str]:
	return config.getKeyOrDefault("channels", list, list[str]())

def getDefaultName() -> str:
	return config.getKeyOrDefault("defaultName", str, "CHAT")

def getActionVotePeriod() -> int:
	return config.getKeyOrDefault("actionVotePeriod", int, 15)

def getOutputOcrImages() -> int:
	return config.getKeyOrDefault("outputOcrImages", bool, False)

def getInstructionsCooldown() -> int:
	return config.getKeyOrDefault("instructionsCooldown", int, 15)

def getRunChatbot() -> bool:
	return config.getKeyOrDefault("runChatbot", bool, True)

def getRunGamebot() -> bool:
	return config.getKeyOrDefault("runGamebot", bool, True)

def getRunOverlay() -> bool:
	return config.getKeyOrDefault("runOverlay", bool, True)

def useSidebarActionOverlay() -> bool:
	return config.getKeyOrDefault("useSidebarActionOverlay", bool, False)