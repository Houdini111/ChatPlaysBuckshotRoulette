from time import sleep

class Rectangle():
	def __init__(self, x: int, y: int, w: int, h: int):
		self.x = x
		self.y = y
		self.w = w
		self.h = h
	
	def __str__(self):
		return "{" + f"x: {self.x}, y: {self.y}, w: {self.w}, y: {self.h}" + "}"

def waitForFalse(checker):
	print("Waiting for method to return false")
	i = 0
	while checker():
		i += 1
		#print(f"Waiting for method to return false. Attempts: {i}", end='\r')
		print(f"Waiting for method to return false. Attempts: {i}")
		sleep(0.1)

def waitForTrue(checker):
	print("Waiting for method to return true")
	i = 0
	while not checker():
		i += 1
		#print(f"Waiting for method to return true. Attempts: {i}", end='\r')
		print(f"Waiting for method to return true. Attempts: {i}")
		sleep(0.1)

def safeInt(inVal: str | int) -> int | None:
	if input is None:
		return None
	elif type(inVal) is int:
		return inVal
	elif type(inVal) is str and inVal.isdigit():
		return int(inVal)
	return None
	