from time import sleep
from typing import Callable
import math

import pyautogui

from .log import log

class Rectangle():
	def __init__(self, x: int, y: int, w: int, h: int):
		self.x = x
		self.y = y
		self.w = w
		self.h = h
	
	def __str__(self) -> str:
		return "{" + f"x: {self.x}, y: {self.y}, w: {self.w}, y: {self.h}" + "}"

def waitForFalse(checker: Callable[[], bool]) -> None:
	log("Waiting for method to return false")
	i = 0
	while checker():
		i += 1
		#log(f"Waiting for method to return false. Attempts: {i}", end='\r')
		log(f"Waiting for method to return false. Attempts: {i}")
		sleep(0.1)

def waitForTrue(checker: Callable[[], bool]) -> None:
	log("Waiting for method to return true")
	i = 0
	while not checker():
		i += 1
		#log(f"Waiting for method to return true. Attempts: {i}", end='\r')
		log(f"Waiting for method to return true. Attempts: {i}")
		sleep(0.1)

def safeInt(inVal: str | int | None, defaultValue: int) -> int:
	if type(inVal) is int:
		return inVal
	elif type(inVal) is str and inVal.isdigit():
		return int(inVal)
	return defaultValue

def resizePointFrom1440p(x1440: int, y1440: int) -> list[int]:
	xPercent = x1440/2560
	yPercent = y1440/1440
	displayW, displayH = pyautogui.size()
	realX = int(math.ceil(xPercent * displayW))
	realY = int(math.ceil(yPercent * displayH))
	return [realX, realY]

def resizeRectFrom1440p(x1440: int, y1440: int, w1440: int, h1440: int) -> list[int]:
	wPercent = w1440/2560
	hPercent = h1440/1440
	displayW, displayH = pyautogui.size()
	realW = int(math.ceil(wPercent * displayW))
	realH = int(math.ceil(hPercent * displayH))
	realX, realY = resizePointFrom1440p(x1440, y1440)
	return [realX, realY, realW, realH]