from time import sleep

from scripts.overlay import getOverlay

from .screenColors import valueOverAmountInArea, valueUnderAmountInArea
from .basicActions import up, right, left, confirm, anyUse
from .focus import waitForFocus
from .status import status
from shared.util import waitForFalse, waitForTrue
from shared.log import log

def throughToGameRoom() -> None:
	getOverlay().clearOldNameLeaderboard()
	enableEndless()
	exitBathroom()
	enterGameRoom()

def doorFullBlack() -> bool:
	#TODO: Convert to peeper
	return valueOverAmountInArea(1, 1435, 641, 40, 5)

def cursorOnBathroomDoor() -> bool:
	up()
	#Targeting top left 
	#TODO: Conver to peeper
	return valueOverAmountInArea(70, 1435, 641, 40, 5)

def moveCursorToBathroomDoor() -> None:
	status("Moving cursor to bathroom door")
	waitForFocus()
	up() #Make cursor show without changing selection
	movements: int = 0
	for movements in range(20): #Tries before movement
		#Give each section 5 tries, in case the check missed
		i: int = 0
		for i in range(1): 
			#Targeting bottom left of cursor. This should be a large enough area to see it, even with the swaying.
			#valueOverAmount = valueOverAmountInArea(50, 1432, 712, 40, 1)
			if cursorOnBathroomDoor():
				return
			sleep(0.1)
		log(f"Didn't find cursor on door. Moving cursor and trying again. Momvent: {movements}")
		right()
	raise RuntimeError("Couldn't locate door cursor")

def enableEndless() -> None:
	status("Enabling endless")
	moveCursorToBathroomDoor()
	left()
	confirm()
	status("Waiting for pills menu to open fully")
	sleep(1.75)
	left()
	confirm()
	status("Pills consumed. Waiting for reload to bathroom.")
	sleep(1.2) #Typically takes 15 0.1 seconds waits for the following to return. To prevent some logspam I'm just going to wait for 1.2 seconds here
	waitForFalse(doorFullBlack)
	sleep(0.5)    #Likewise, but 8 0.1 second waits, so waiting 0.5 seconds here.
	waitForTrue(cursorOnBathroomDoor)

def exitBathroom() -> None:
	status("Exiting bathroom")
	anyUse()
	sleep(5.5) #Do I need more? Can I get away with less?
	
def enterGameRoom() -> None:
	status("Entering game room")
	anyUse()
	sleep(10) #Do I need more? Can I get away with less?

def inStartingBathroom() -> bool:
	#TODO: Is this reliable enough of a check? All the swaying and grays makes it really hard to tell...
	#TODO: Convert to Peepers
	log("Checking for if the player is in the bathroom.")
	monitorHoleBlack = valueUnderAmountInArea(1, 342, 497, 50, 50)
	if not monitorHoleBlack:
		log("Found to not be in the starting bathroom because of monitorHoleBlack")
		return False
	monitorScreenBlack = valueUnderAmountInArea(1, 533, 781, 50, 50)
	if not monitorScreenBlack:
		log("Found to not be in the starting bathroom because of monitorScreenBlack")
		return False
	mirrorOffWhite1 = valueOverAmountInArea(80, 246, 290, 35, 35)
	if not mirrorOffWhite1:
		log("Found to not be in the starting bathroom because of mirrorOffWhite1")
		return False
	mirrorOffWhite2 = valueOverAmountInArea(80, 444, 315, 35, 35)
	if not mirrorOffWhite2:
		log("Found to not be in the starting bathroom because of mirrorOffWhite2")
		return False
	mirrorOffWhite3 = valueOverAmountInArea(80, 113, 278, 35, 35)
	if not mirrorOffWhite3:
		log("Found to not be in the starting bathroom because of mirrorOffWhite3")
		return False
	#tilesAboveDoorGray = valueOverAmountInArea
	return True