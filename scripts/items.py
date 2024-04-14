from time import sleep
import json

from .basicActions import enterDirections, confirm, up
from .screenColors import valueOverAmountInArea
from .status import removeAllTempStatus, status, tempStatus
from shared.log import log

currentItemPositions: list[int]		= []

def getAllCurrentItemPositions() -> list[int]:
	return currentItemPositions

def getNextOpenItemPosition() -> int:
	positionsStr: str = ""
	for pos in currentItemPositions:
		positionsStr += str(pos) + ", "
	if len(positionsStr) > 2:
		positionsStr = positionsStr[0: -2]
	log(f"Current item positions: [{positionsStr}]")
	for i in range(1, 9): #[1, 8]
		if i not in currentItemPositions:
			log(f"Next item position found: {i}")
			return i
	log("ERROR: NO FREE SLOT FOUND")
	return 0

def clearItems() -> None:
	global currentItemPositions
	log("Clearing current items")
	currentItemPositions.clear()

def removeItem(num: int) -> None:
	global currentItemPositions
	currentItemPositions.remove(num)
	log(f"Removing item {num}. Remaining items: {json.dumps(currentItemPositions)}")

def putItemAt(place: int) -> None:
	global currentItemPositions
	enterDirections(getPlayerItemDirections(place, "pickup"))
	confirm()
	currentItemPositions.append(place)

def itemAtPosition(pos: int) -> bool:
	#TODO: Eventually return the actual item Enum/Class, rather than just saying one exists
	return pos in currentItemPositions

def grabItems() -> None:
	tempStatus("Trying to grab items")
	if not itemBoxIsOpen():
		log("Item box not yet open. Waiting.")
	while not itemBoxIsOpen():
		sleep(0.25)
	log("Item box open, waiting for cursor.")
	waitForItemBoxCursorVisible()
	while itemBoxIsOpen():
		tempStatus("Grabbing item from box")
		confirm()
		tempStatus("Waiting for item to be pulled out")
		sleep(0.5)
		nextPosition = getNextOpenItemPosition()
		if nextPosition == 0:
			log("Supposedly there's no free slots. The game should be saying the same thing to the player now. Ending grabItems loop.")
			break
		putItemAt(nextPosition)
		sleep(0.25) #A tiny wait while the item moves away from the box
		tempStatus("Waiting for item to be placed and or box close animation")
		while itemBoxIsOpen() and not itemBoxCursorVisible():
			sleep(0.1)
	removeAllTempStatus()
	log("All items withdrawn.")
	#TODO: When player turn after grabbing items, don't allow player movmement first. 
	#   Hover over every item and OCR to find what they are so we can more intelligently handle their usage times and requirements (adrenaline)

def itemBoxIsOpen() -> bool:
	#TODO: Convert to Peepers
	log("Checking for item box open")
	itemBoxBlackVisible = not valueOverAmountInArea(1, 1018, 468, 30, 100)
	if not itemBoxBlackVisible:
		log("Item box not visible. No item box black found.")
		return False
	bulletBoxWhiteVisible = valueOverAmountInArea(95, 1525, 23, 30, 30)
	if not bulletBoxWhiteVisible:
		log("Item box not visible. No bullet square white found.")
		return False
	centerLineVisible = valueOverAmountInArea(95, 569, 68, 10, 10)
	if not bulletBoxWhiteVisible:
		log("Item box not visible. No center line white found.")
		return False
	return True

def waitForItemBoxCursorVisible() -> None:
	while not itemBoxCursorVisible():
		sleep(0.1)

def itemBoxCursorVisible() -> bool:
	log("Checking for item box cursor. First checking for box open.")
	if not itemBoxIsOpen():
		log("Item box cursor not visible as item bot not found open.")
		return False
	up()
	#TODO: Convert to Peepers
	cursorVisible = valueOverAmountInArea(90, 956, 950, 47, 1) #Targeting bottom left of bracket
	log(f"Item box cursor visible: {cursorVisible}")
	return cursorVisible



def getPlayerItemDirections(num: int, mode: str) -> list[str]:
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
	log(f"Item directions for item {num} in mode: {mode} -> {directions}")
	return directions

def getDealerItemDirections(num: int) -> list[str]:
	#Starts on 6
	if num == 6:
		log("Requested dealer item 6, the starting position. No extra movements")
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
	log(f"Dealer item directions for {num} -> {directions}")
	return directions