from time import sleep
from typing import Callable

class Rectangle():
	def __init__(self, x: int, y: int, w: int, h: int):
		self.x = x
		self.y = y
		self.w = w
		self.h = h
	
	def __str__(self) -> str:
		return "{" + f"x: {self.x}, y: {self.y}, w: {self.w}, y: {self.h}" + "}"

def waitForFalse(checker: Callable[[], bool]) -> None:
	print("Waiting for method to return false")
	i = 0
	while checker():
		i += 1
		#print(f"Waiting for method to return false. Attempts: {i}", end='\r')
		print(f"Waiting for method to return false. Attempts: {i}")
		sleep(0.1)

def waitForTrue(checker: Callable[[], bool]) -> None:
	print("Waiting for method to return true")
	i = 0
	while not checker():
		i += 1
		#print(f"Waiting for method to return true. Attempts: {i}", end='\r')
		print(f"Waiting for method to return true. Attempts: {i}")
		sleep(0.1)

def safeInt(inVal: str | int | None, defaultValue: int) -> int:
	if type(inVal) is int:
		return inVal
	elif type(inVal) is str and inVal.isdigit():
		return int(inVal)
	return defaultValue
	