from time import sleep
import json

from .basicActions import enterDirections, confirm, up
from .screenColors import valueOverAmountInArea
from shared.log import log
from shared.actions import setItemAtPositionFunc
from overlay.status import removeAllTempStatus, status, tempStatus
	
class ItemManager(): 
	def __init__(self):
		self.currentItemPositions: list[int] = list[int]()
		setItemAtPositionFunc(self.itemAtPosition)
		
	def getAllCurrentItemPositions(self) -> list[int]:
		return self.currentItemPositions

	def getNextOpenItemPosition(self) -> int:
		positionsStr: str = ""
		for pos in self.currentItemPositions:
			positionsStr += str(pos) + ", "
		if len(positionsStr) > 2:
			positionsStr = positionsStr[0: -2]
		log(f"Current item positions: [{positionsStr}]")
		for i in range(1, 9): #[1, 8]
			if i not in self.currentItemPositions:
				log(f"Next item position found: {i}")
				return i
		log("ERROR: NO FREE SLOT FOUND")
		return 0

	def clearItems(self) -> None:
		log("Clearing current items")
		self.currentItemPositions.clear()

	def removeItem(self, num: int) -> None:
		self.currentItemPositions.remove(num)
		log(f"Removing item {num}. Remaining items: {json.dumps(self.currentItemPositions)}")

	def putItemAt(self, place: int) -> None:
		enterDirections(getPlayerItemDirections(place, "pickup"))
		confirm()
		self.currentItemPositions.append(place)

	def itemAtPosition(self, pos: int) -> bool:
		#TODO: Eventually return the actual item Enum/Class, rather than just saying one exists
		return pos in self.currentItemPositions

	def grabItems(self) -> None:
		tempStatus("Trying to grab items")
		if not self.itemBoxIsOpen():
			log("Item box not yet open. Waiting.")
		while not self.itemBoxIsOpen():
			sleep(0.25)
		log("Item box open, waiting for cursor.")
		self.waitForItemBoxCursorVisible()
		while self.itemBoxIsOpen():
			tempStatus("Grabbing item from box")
			confirm()
			tempStatus("Waiting for item to be pulled out")
			sleep(0.5)
			nextPosition = self.getNextOpenItemPosition()
			if nextPosition == 0:
				log("Supposedly there's no free slots. The game should be saying the same thing to the player now. Ending grabItems loop.")
				break
			self.putItemAt(nextPosition)
			sleep(0.25) #A tiny wait while the item moves away from the box
			tempStatus("Waiting for item to be placed and or box close animation")
			while self.itemBoxIsOpen() and not self.itemBoxCursorVisible():
				sleep(0.1)
		removeAllTempStatus()
		log("All items withdrawn.")
		#TODO: When player turn after grabbing items, don't allow player movmement first. 
		#   Hover over every item and OCR to find what they are so we can more intelligently handle their usage times and requirements (adrenaline)

	def itemBoxIsOpen(self) -> bool:
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

	def waitForItemBoxCursorVisible(self) -> None:
		while not self.itemBoxCursorVisible():
			sleep(0.1)

	def itemBoxCursorVisible(self) -> bool:
		log("Checking for item box cursor. First checking for box open.")
		if not self.itemBoxIsOpen():
			log("Item box cursor not visible as item bot not found open.")
			return False
		up()
		#TODO: Convert to Peepers
		cursorVisible = valueOverAmountInArea(90, 956, 950, 47, 1) #Targeting bottom left of bracket
		log(f"Item box cursor visible: {cursorVisible}")
		return cursorVisible

itemManager: ItemManager | None = None
def getItemManager():
	global itemManager
	if itemManager is None:
		itemManager = ItemManager()
	return itemManager

def getPlayerItemDirections(num: int, mode: str) -> list[str]:
	verticalOffset: list[str] = list[str]()
	horizontalOffset: list[str] = list[str]()
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
		return list[str]()
	horizontalOffset: list[str] = list[str]()
	verticalOffset: list[str] = list[str]()
	
	if num == 1 or num == 5:
		horizontalOffset = ['l']
	elif num == 3 or num == 7:
		horizontalOffset = ['r']
	elif num == 4 or num == 8:
		horizontalOffset = ['r', 'r']
	
	if num >= 1 and num <= 4:
		verticalOffset = ['u']
	
	directions: list[str] = horizontalOffset + verticalOffset
	log(f"Dealer item directions for {num} -> {directions}")
	return directions