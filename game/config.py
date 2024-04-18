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
	
	def getKeyOrDefault(self, key: str, expectedType: type[T], defaultValue: T) -> T:
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