from time import sleep
import colorsys

import screenColors
import basicActions
import focus
import util

def throughToGameRoom():
	enableEndless()
	exitBathroom()
	enterGameRoom()

def doorFullBlack():
	#TODO: Convert to peeper
	return screenColors.valueOverAmountInArea(1, 1435, 641, 40, 5)

def cursorOnBathroomDoor():
	basicActions.up()
	#Targeting top left 
	#TODO: Conver to peeper
	return screenColors.alueOverAmountInArea(70, 1435, 641, 40, 5)

def moveCursorToBathroomDoor():
	print("### Moving cursor to bathroom door")
	focus.waitFocused()
	basicActions.up() #Make cursor show without changing selection
	for movements in range(20): #Tries before movement
		#Give each section 5 tries, in case the check missed
		for i in range(1): 
			#Targeting bottom left of cursor. This should be a large enough area to see it, even with the swaying.
			#valueOverAmount = valueOverAmountInArea(50, 1432, 712, 40, 1)
			if cursorOnBathroomDoor():
				return
			sleep(0.1)
		print("Didn't find cursor on door. Moving cursor and trying again.")
		basicActions.right()
	raise Exception("Couldn't locate door cursor")

def enableEndless():
	print("##### Enabling endless")
	moveCursorToBathroomDoor()
	basicActions.left()
	basicActions.confirm()
	print("Waiting for pills menu to open fully")
	sleep(1.75)
	basicActions.left()
	basicActions.confirm()
	print("Pills consumed. Waiting for reload to bathroom.")
	basicActions.waitForFalse(doorFullBlack)
	util.waitForTrue(cursorOnBathroomDoor)

def exitBathroom():
	print("##### Exiting bathroom")
	basicActions.anyUse()
	sleep(5.5) #Do I need more? Can I get away with less?
	
def enterGameRoom():
	print("##### Entering game room")
	basicActions.anyUse()
	sleep(10) #Do I need more? Can I get away with less?

def inStartingBathroom():
	#TODO: Is this reliable enough of a check? All the swaying and grays makes it really hard to tell...
	#TODO: Convert to Peepers
	print("### Checking for if the player is in the bathroom.")
	monitorHoleBlack = screenColors.valueUnderAmountInArea(1, 342, 497, 50, 50)
	if not monitorHoleBlack:
		print("### Found to not be in the starting bathroom because of monitorHoleBlack")
		return False
	monitorScreenBlack = screenColors.valueUnderAmountInArea(1, 533, 781, 50, 50)
	if not monitorScreenBlack:
		print("### Found to not be in the starting bathroom because of monitorScreenBlack")
		return False
	mirrorOffWhite1 = screenColors.valueOverAmountInArea(80, 246, 290, 35, 35)
	if not mirrorOffWhite1:
		print("### Found to not be in the starting bathroom because of mirrorOffWhite1")
		return False
	mirrorOffWhite2 = screenColors.valueOverAmountInArea(80, 444, 315, 35, 35)
	if not mirrorOffWhite2:
		print("### Found to not be in the starting bathroom because of mirrorOffWhite2")
		return False
	mirrorOffWhite3 = screenColors.valueOverAmountInArea(80, 113, 278, 35, 35)
	if not mirrorOffWhite3:
		print("### Found to not be in the starting bathroom because of mirrorOffWhite3")
		return False
	#tilesAboveDoorGray = valueOverAmountInArea
	return True