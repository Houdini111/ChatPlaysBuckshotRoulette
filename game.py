from time import sleep
from basicActions import confirm, left, right, up, down, enterDirections, anyUse
from screenColors import getPixelAreaAverageBy1440p



currentItemPositions = []



def cursorGun():
	up()
	up()
	
def cursorItem(num):
	cursorGun()
	enterDirections(getItemDirections(num, True))

def useGun():
	cursorGun()
	confirm()

def useItem(num):
	cursorItem(num)
	confirm()
	
def chooseDealer():
	up()
	confirm()

def chooseSelf():
	down()
	confirm()
	
def getItemDirections(num: int, gunMode: bool):
	verticalOffset = []
	horizontalOffset = []
	if num == 1 or num == 5:
		horizontalOffset = ['l', 'l']
	elif num == 2 or num == 6:
		horizontalOffset = ['l']
	elif num == 3 or num == 7:
		horizontalOffset = ['r']
	elif num == 4 or num == 8:
		horizontalOffset = ['r', 'r']
	
	if gunMode: #item use mode
		if num >= 5 and num <= 8:
			verticalOffset = ['d']
	else: #item pickup mode
		if num >= 1 and num <= 4:
			verticalOffset = ['u']
	directions = horizontalOffset + verticalOffset
	print(f"Item directions for item {num} in gunMode: {gunMode} == {directions}")
	return directions
	
def itemBoxIsOpen():
	#Targeting the dark shadow on the left of the box
	areaColor = getPixelAreaAverageBy1440p(1025, 467, 10, 10)
	r, g, b = areaColor
	#I have yet to see this anything other than true black, but add a bit of wiggle room in case
	return r < 5 and g < 5 and b < 5

def getOpenItemPosition():
	for i in range(1, 9): #[1, 8]
		if i not in currentItemPositions:
			return i
	print("ERRROR: NO FREE SLOT FOUND")
	return 1

def putItemAt(place):
	enterDirections(getItemDirections(place, False))
	confirm()
	currentItemPositions.append(place)

def grabItems():
	if not itemBoxIsOpen():
		print("Item box not yet open. Waiting.")
	while not itemBoxIsOpen():
		sleep(0.25)
	sleep(1) #Sleep for a little extra because of the interactive delay
	while itemBoxIsOpen():
		print("Grabbing item from box")
		anyUse()
		print("Waiting for item to be pulled out")
		sleep(1)
		nextPosition = getOpenItemPosition()
		putItemAt(nextPosition)
		print("Waiting for place and or box close animation")
		sleep(1)
	print("All items withdrawn. Waiting for loading animation.")
	sleep(11.5) #Maximum wait time assumes 8 shells to loading

def awaitInputs():
	while(True):
		request = input("Next? ")
		request = request.lower().strip()
		splitRequest = request.split(' ')
		action = splitRequest[0]
		param = ""
		extraParam = ""
		if len(splitRequest) > 1:
			param = splitRequest[1]
		if len(splitRequest) > 2:
			extraParam = splitRequest[2]
			
		if action == 'use' or action == 'item':
			useItem(int(param))
			if extraParam != "":
				print("Extra param given (presumably for adrenaline). Wait for adrenaline usage and movement.")
				sleep(7)
				useItem(int(extraParam))
		elif action == 'shoot':
			useGun()
			sleep(1)
			if param == 'self':
				chooseSelf()
			elif param == 'dealer':
				chooseDealer()
			else:
				print(f"UNRECOGNIZED TARGET \"{param}\"")
		elif action == 'take':
			grabItems()
		else:
			print(f"UNRECOGNIZED ACTION \"{action}\"")