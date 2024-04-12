from time import sleep

import basicActions
import gameRunner
import screenColors

currentItemPositions = []

def getOpenItemPosition():
	for i in range(1, 9): #[1, 8]
		if i not in currentItemPositions:
			return i
	print("ERROR: NO FREE SLOT FOUND")
	return 0

def clearItems():
	global currentItemPositions
	currentItemPositions.clear()

def putItemAt(place):
	global currentItemPositions
	basicActions.enterDirections(getItemDirections(place, "pickup"))
	basicActions.confirm()
	currentItemPositions.append(place)

def itemAtPosition(pos: int) -> bool:
	#TODO: Eventually return the actual item Enum/Class, rather than just saying one exists
	return pos in currentItemPositions

def grabItems():
	print("### Trying to grab items")
	if not itemBoxIsOpen():
		print("Item box not yet open. Waiting.")
	while not itemBoxIsOpen():
		sleep(0.25)
	print("Item box open, waiting for cursor.")
	waitForItemBoxCursorVisible()
	while itemBoxIsOpen():
		print("Grabbing item from box")
		basicActions.confirm()
		print("Waiting for item to be pulled out")
		sleep(0.5)
		nextPosition = getOpenItemPosition()
		if nextPosition == 0:
			print("Supposedly there's no free slots. The game should be saying the same thing to the player now. Ending grabItems loop.")
			break
		putItemAt(nextPosition)
		sleep(0.25) #A tiny wait while the item moves away from the box
		print("Waiting for item to be placed and or box close animation")
		while itemBoxIsOpen() and not itemBoxCursorVisible():
			sleep(0.1)
	print("All items withdrawn.")
	#TODO: When player turn after grabbing items, don't allow player movmement first. 
	#   Hover over every item and OCR to find what they are so we can more intelligently handle their usage times and requirements (adrenaline)

def itemBoxIsOpen():
	#TODO: Convert to Peepers
	print("## Checking for item box open")
	itemBoxBlackVisible = not screenColors.valueOverAmountInArea(1, 1018, 468, 30, 100)
	if not itemBoxBlackVisible:
		print("## Item box not visible. No item box black found.")
		return False
	bulletBoxWhiteVisible = screenColors.valueOverAmountInArea(95, 1525, 23, 30, 30)
	if not bulletBoxWhiteVisible:
		print("## Item box not visible. No bullet square white found.")
		return False
	centerLineVisible = screenColors.valueOverAmountInArea(95, 569, 68, 10, 10)
	if not bulletBoxWhiteVisible:
		print("## Item box not visible. No center line white found.")
		return False
	return True

def waitForItemBoxCursorVisible():
	while not itemBoxCursorVisible():
		sleep(0.1)

def itemBoxCursorVisible():
	print("## Checking for item box cursor. First checking for box open.")
	if not itemBoxIsOpen():
		print("## Item box cursor not visible as item bot not found open.")
		return False
	basicActions.up()
	#OTOD: Convert to Peepers
	cursorVisible = screenColors.valueOverAmountInArea(90, 956, 950, 47, 1) #Targeting bottom left of bracket
	print(f"## Item box cursor visible: {cursorVisible}")
	return cursorVisible



def getItemDirections(num: int, mode: str):
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
	
	if mode == "use":
		if num >= 5 and num <= 8:
			verticalOffset = ['d']
	elif mode == "pickup":
		if num >= 1 and num <= 4:
			verticalOffset = ['u']
	directions = horizontalOffset + verticalOffset
	print(f"Item directions for item {num} in mode: {mode} -> {directions}")
	return directions

def getDealerItemDirections(num: int):
	#Starts on 6
	if num == 6:
		print("Requested dealer item 6, the starting position. No extra movements")
		return []
	horizontalOffset = []
	verticalOffset = []
	
	if num == 1 or num == 5:
		horizontalOffset = ['l']
	elif num == 3 or num == 7:
		horizontalOffset = ['r']
	elif num == 4 or num == 8:
		horizontalOffset = ['r', 'r']
	
	if num >= 1 and num <= 4:
		verticalOffset = ['u']
	
	directions = horizontalOffset + verticalOffset
	print(f"Dealer item directions for {num} -> {directions}")
	return directions