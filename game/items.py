import logging
import math
from time import sleep

from .basicActions import enterDirections, confirm, up
from .screenColors import valueOverAmountInArea
from .pixelPeep import Peeper, AnyWhitePeep, AllBlackPeep, AnyNotBlackPeep
from shared.actions import setItemAtPositionFunc
from overlay.status import removeAllTempStatus, status, tempStatus
	
logger = logging.getLogger(__name__)

class ItemManager(): 
	def __init__(self):
		self.currentItemPositions: list[int] = list[int]()
		setItemAtPositionFunc(self.itemAtPosition)
		
		self.itemNamePeeper = Peeper("ItemNamePeeper", 
			AnyWhitePeep("AnyWhitePixelsItemTextNamePeep", 1075, 1089, 413, 52),
			AllBlackPeep("ItemBoardStaticLeftAllBlackPeep", 219, 541, 24, 24),
			AllBlackPeep("ItemBoardStaticRightAllBlackPeep", 2406, 637, 24, 24),
			AnyWhitePeep("ItemBoardStaticAnyWhitePeep", 1474, 392, 26, 26)
		)
		
		self.itemBoxOpenPeeper = Peeper("ItemBoxOpenPeeper", 
			AllBlackPeep("ItemBoxBlackVisiblePeep", 1580, 932, 25, 25),
			AnyWhitePeep("BulletBoxWhiteVisiblePeep", 1525, 23, 30, 30),
			AnyWhitePeep("CenterLineWhiteVisiblePeep", 569, 68, 10, 10)
		)
		
		self.itemBoxItemPeeper = Peeper("ItemBoxItemPeeper", 
			AnyNotBlackPeep("ItemAnyNotBlackPeep", 1286, 680, 35, 35),
			self.itemBoxOpenPeeper
		)
		
	def getAllCurrentItemPositions(self) -> list[int]:
		logger.info(f"Getting all current itme positions: {self.currentItemPositions}")
		return self.currentItemPositions

	def getNextOpenItemPosition(self) -> int:
		logger.info("Finding next open item position")
		positionsStr: str = ""
		for pos in self.currentItemPositions:
			positionsStr += str(pos) + ", "
		if len(positionsStr) > 2:
			positionsStr = positionsStr[0: -2]
		logger.debug(f"Current item positions: [{positionsStr}]")
		for i in range(1, 9): #[1, 8]
			if i not in self.currentItemPositions:
				logger.debug(f"Next item position found: {i}")
				return i
		logger.warn("NO FREE ITEM SLOT FOUND")
		return 0

	def clearItems(self) -> None:
		logger.info("Clearing current items")
		self.currentItemPositions.clear()

	def removeItem(self, num: int) -> None:
		logger.info(f"Removing item {num}")
		logger.debug(f"Removing item {num}. Before items: {self.currentItemPositions}")
		self.currentItemPositions.remove(num)
		logger.debug(f"Removing item {num}. After items: {self.currentItemPositions}")

	def putItemAt(self, place: int) -> bool:
		logger.info(f"Putting item at {place}")
		enterDirections(getPlayerItemDirections(place, "pickup"))
		success: bool = self.placeItem()
		if success: 
			self.currentItemPositions.append(place)
		return success
	
	def placeItem(self) -> bool:
		logger.info("Placing item at current position")
		confirm()
		sleep(0.15) #Wait for item to start moving
		if self.itemBoxIsOpen() and self.itemBoxItemPeeper.passes():
			#If it still sees the item, then it failed to place there
			return False
		return True

	def itemAtPosition(self, pos: int) -> bool:
		logger.info(f"itemAtPosition: {pos}")
		atPosition: bool = pos in self.currentItemPositions
		logger.debug(f"Is item {pos} currently in the list of current items ({self.currentItemPositions})? {atPosition}")
		#TODO: Eventually return the actual item Enum/Class, rather than just saying one exists
		return atPosition

	def grabItems(self) -> None:
		tempStatus("Trying to grab items")
		if not self.itemBoxIsOpen():
			logger.info("Item box not yet open. Waiting.")
		while not self.itemBoxIsOpen():
			sleep(0.25)
		logger.info("Item box open, waiting for cursor.")
		self.waitForItemBoxCursorVisible()
		while self.itemBoxIsOpen():
			tempStatus("Grabbing item from box")
			confirm()
			tempStatus("Waiting for item to be pulled out")
			sleep(0.5)
			nextPosition = self.getNextOpenItemPosition()
			if nextPosition == 0:
				logger.info("Supposedly there's no free slots. The game should be saying the same thing to the player now. Ending grabItems loop.")
				break
			self.putItemAt(nextPosition)
			sleep(0.25) #A tiny wait while the item moves away from the box
			tempStatus("Waiting for item to be placed and or box close animation")
			while self.itemBoxIsOpen() and not self.itemBoxCursorVisible():
				sleep(0.1)
		removeAllTempStatus()
		logger.info("All items withdrawn")
		#TODO: When player turn after grabbing items, don't allow player movmement first. 
		#   Hover over every item and OCR to find what they are so we can more intelligently handle their usage times and requirements (adrenaline)

	def grabItemsV2(self) -> None:
		tempStatus("Trying to grab items")
		if not self.itemBoxIsOpen():
			logger.info("Item box not yet open. Waiting.")
		while not self.itemBoxIsOpen():
			sleep(0.25)
		logger.info("Item box open, waiting for cursor.")
		self.waitForItemBoxCursorVisible()
		i: int = 1
		while self.itemBoxIsOpen():
			tempStatus("Grabbing item from box")
			confirm()
			tempStatus("Waiting for item to be pulled out")
			sleep(0.5) #TODO: Use actual check instead of time
			succeeded: bool = False
			succeeded = self.putItemAt(i)
			while not succeeded and i < 9:
				enterDirections(getPlacePositionDirectionsFrom(i, i + 1, False))
				succeeded = self.placeItem()
				i += 1
			if succeeded:
				i += 1 #Move it forward so the next item doesn't try to get place here
			else:
				logger.warn("Failed to place item. No more slots to be found. The game should be saying the same thing to the player now. Ending grabItems loop.")
				break
			#sleep(0.25) #A tiny wait while the item moves away from the box
			tempStatus("Waiting for item to be placed and or box close animation")
			while self.itemBoxIsOpen() and not self.itemBoxCursorVisible():
				sleep(0.1)
		removeAllTempStatus()
		logger.info("All items withdrawn")

	def itemBoxIsOpen(self) -> bool:
		logger.info("Checking for item box open")
		return self.itemBoxOpenPeeper.passes()

	def waitForItemBoxCursorVisible(self) -> None:
		while not self.itemBoxCursorVisible():
			sleep(0.1)

	def itemBoxCursorVisible(self) -> bool:
		logger.info("Checking for item box cursor. First checking for box open.")
		if not self.itemBoxIsOpen():
			logger.debug("Item box cursor not visible as item bot not found open.")
			return False
		up()
		#TODO: Convert to Peepers
		cursorVisible = valueOverAmountInArea(90, 956, 950, 47, 1) #Targeting bottom left of bracket
		logger.debug(f"Item box cursor visible: {cursorVisible}")
		return cursorVisible
	
	def refreshPlayerItems(self) -> None:
		status("Refreshing player items")
		self.currentItemPositions.clear()
		#Select slot 1
		logger.debug("Item positions cleared. Moving to #1")
		enterDirections("u", "u", "l", "l")
		for i in range(1, 9): #[1, 9)
			logger.debug(f"Refreshing for item at position {i}")
			enterDirections(getPlacePositionDirectionsFrom(i - 1, i, True)) 
			sleep(0.075) #Wait for the (very fast) fade in of text
			if self.itemNamePeeper.passes():
				logger.debug(f"Item found at position {i}")
				self.currentItemPositions.append(i)
			else: 
				logger.debug(f"No item found at position {i}")
		logger.info(f"Found items at positions: {self.currentItemPositions}")
		
		

itemManager: ItemManager | None = None
def getItemManager():
	global itemManager
	if itemManager is None:
		itemManager = ItemManager()
	return itemManager

def getPlayerItemDirections(num: int, mode: str) -> list[str]:
	logger.info(f"Getting item directions for player items to position: {num} and mode: {mode}")
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
	logger.debug(f"Item directions for item {num} in mode: {mode} are {directions}")
	return directions

def getDealerItemDirections(num: int) -> list[str]:
	logger.info(f"Getting item directions for dealer items to position: {num}")
	#Starts on 6
	if num == 6:
		logger.debug("Requested dealer item 6, the starting position. No extra movements")
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
	logger.debug(f"Dealer item directions for {num} are {directions}")
	return directions

def getPlacePositionDirectionsFrom(fromPos: int, toPos: int, includeGun: bool) -> list[str]:
	logger.debug(f"Calculating direction to move from {fromPos} to place item at {toPos}")
	if fromPos <= 0 or fromPos > 8 or toPos <= 0 or toPos > 8:
		logger.debug("Asked for to or from position out of range. Returning no directions.")
		return list[str]()

	horizontalInstructions: list[str] = list[str]()
	verticalInstructions: list[str] = list[str]()
	
	#Positions are 1 indexed while these operations only really work with 0 indexed
	fromPos0Index: int = fromPos - 1
	toPos0Index: int = toPos - 1
	toColumn: int = toPos0Index % 4
	fromColumn: int = fromPos0Index % 4
	toRow: int = int(math.floor(toPos0Index/4))
	fromRow: int = int(math.floor(fromPos0Index/4))
	logger.debug(f"fromPos {fromPos}: [{fromColumn}, {fromRow}] -> toPos {toPos}: [{toColumn}, {toRow}] ")
	
	horizontalDiff: int = toColumn - fromColumn
	if horizontalDiff != 0:
		diffChar: list[str] = list[str]("")
		if horizontalDiff < 0: 
			diffChar = list[str]("l")
		elif horizontalDiff > 0:
			diffChar = list[str]("r")
		horizontalInstructions = diffChar * abs(horizontalDiff)

	verticalDiff: int = toRow - fromRow
	if verticalDiff < 0:
		verticalInstructions = list[str]("u")
	elif verticalDiff > 0:
		verticalInstructions = list[str]("d")
		
	if includeGun:
		if fromPos in (1, 2) and toPos in (3, 4, 7, 8):
			logger.debug("Directions will move past gun. Adding extra right movement to compensate.")
			horizontalInstructions.append("r")
		elif fromPos in (3, 4) and toPos in (1, 2, 5, 6):
			logger.debug("Directions will move past gun. Adding extra left movement to compensate.")
			horizontalInstructions.append("l")


	logger.debug(f"horizontalDiff: {horizontalDiff} -> {horizontalInstructions} verticalDiff: {verticalDiff} -> {verticalInstructions}")

	instructions: list[str] = horizontalInstructions + verticalInstructions
	logger.debug(f"Item directiion to move from {fromPos} to place item at {toPos} are -> {instructions}")
	return instructions