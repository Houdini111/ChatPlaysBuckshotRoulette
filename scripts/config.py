import json
import os
from typing import TypeVar
from typing_extensions import TypeAlias

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
		if val is expectedType:
			return val
		raise ValueError(f"Val: |{val}| was not None or expected type {expectedType} but was of type {val}")

config: Config = Config()

def getTesseractPath() -> str:
	return config.getKeyOrDefault("tesseractPath", type(str), r"C:\Program Files\Tesseract-OCR\tesseract")