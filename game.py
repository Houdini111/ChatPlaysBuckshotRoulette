from time import sleep
import colorsys
from basicActions import confirm, left, right, up, down, enterDirections, anyUse
from screenColors import getPixelAreaAverageBy1440p, getPixelAreaBy1440p, pixelsMatch, valueOverAmountInArea
from waiver import getPlayerName
from image import scoreboardText
from bathroom import inStartingBathroom



currentItemPositions = []
roundsCleared = 0




#TODO: 
#  Item place logic sometimes skipping squares
#  Sometimes activating endless goes to leaderboards instead

def cursorGun():
	up()
	up()
	
def cursorItem(num):
	cursorGun()
	enterDirections(getItemDirections(num, "use"))

def useGun():
	cursorGun()
	confirm()

def usePersonalItem(num):
	global currentItemPositions
	cursorItem(num)
	confirm()
	currentItemPositions.remove(num)
	print("Waiting for item use animation")
	#Is there a good way to check for which item it is to only wait as long as needed? 
	#This long of a wait might conflict with adrenaline
	sleep(6) #Has to be extra long for phone. 
	print("Item use animation should be over")

def useDealerItem(num):
	down() #Move to ensure cursor is active
	enterDirections(getDealerItemDirections(num))
	confirm()
	
def chooseDealer():
	up()
	confirm()

def chooseSelf():
	down()
	confirm()
	
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
	
def itemBoxIsOpen():
	print("## Checking for item box open")
	itemBoxBlackVisible = not valueOverAmountInArea(1, 1018, 468, 30, 100)
	if not itemBoxBlackVisible:
		print("## Item box not visible. No item box black found.")
		return False
	bulletBoxWhiteVisible = valueOverAmountInArea(95, 1525, 23, 30, 30)
	if not bulletBoxWhiteVisible:
		print("## Item box not visible. No bullet square white found.")
		return False
	centerLineVisible = valueOverAmountInArea(95, 569, 68, 10, 10)
	if not bulletBoxWhiteVisible:
		print("## Item box not visible. No center line white found.")
		return False
	return True

def itemBoxCursorVisible():
	print("## Checking for item box cursor. First checking for box open.")
	if not itemBoxIsOpen():
		print("## Item box cursor not visible as item bot not found open.")
		return False
	up()
	cursorVisible = valueOverAmountInArea(90, 956, 950, 47, 1) #Targeting bottom left of bracket
	print(f"## Item box cursor visible: {cursorVisible}")
	return cursorVisible

def getOpenItemPosition():
	for i in range(1, 9): #[1, 8]
		if i not in currentItemPositions:
			return i
	print("ERRROR: NO FREE SLOT FOUND")
	return 1

def putItemAt(place):
	global currentItemPositions
	enterDirections(getItemDirections(place, "pickup"))
	confirm()
	currentItemPositions.append(place)

def waitForItemBoxCursorVisible():
	while not itemBoxCursorVisible():
		sleep(0.1)

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
		confirm()
		print("Waiting for item to be pulled out")
		sleep(0.5)
		nextPosition = getOpenItemPosition()
		putItemAt(nextPosition)
		sleep(0.25) #A tiny wait while the item moves away from the box
		print("Waiting for item to be placed and or box close animation")
		while itemBoxIsOpen() and not itemBoxCursorVisible():
			sleep(0.1)
	print("All items withdrawn.")

def noDialogueTextBoxVisible():
	print("# Checking for no dialogue box")
	noDialogueLeft = valueOverAmountInArea(1, 577, 1144, 11, 173)
	noDialogueRight = valueOverAmountInArea(1, 1972, 1153, 11, 173)
	print(f"# Dialogue box check: Left {noDialogueLeft} and right {noDialogueRight}")
	return noDialogueLeft and noDialogueRight

def staticBoard():
	print("## Checking for static board")
	print("Checking for black top")
	blackTop = not valueOverAmountInArea(1, 1159, 31, 168, 1)
	if not blackTop: 
		print("## Failed static board check on black top")
		return False
	print("Checking for black left")
	blackLeft = not valueOverAmountInArea(1, 3, 488, 12, 12)
	if not blackLeft: 
		print("## Failed static board check on black left")
		return False
	print("Checking for bullet square")
	bulletSquare = valueOverAmountInArea(95, 1477, 389, 50, 53)
	if not bulletSquare: 
		print("## Failed static board check on bullet square")
		return False
	print("Checking for scoreboard black")
	scoreboardBlack = not valueOverAmountInArea(1, 2040, 347, 5, 5)
	print("Checking that no dialogue text box found")
	noDialogueTextBox = noDialogueTextBoxVisible()
	if not noDialogueTextBox: 
		print("## Failed static board check on check for absence of dialogue box")
		return False
	print("##Passed all static board checks")
	#print(f"Static check-> blackTop: {blackTop}  blackLeft: {blackLeft}  bulletSquare: {bulletSquare}  scoreboardBlack: {scoreboardBlack}  noDialogueTextBox: {noDialogueTextBox}")
	return True

def playerTurn():
	print("### Beginning player turn check")
	if not staticBoard():
		print("Failed player turn check on first static board check")
		return False
	up()
	if not gunCursorVisible():
		print("Failed player turn  check on first gun cursor check")
		return False
	sleep(0.1)
	#Double check to try to avoid coincidences
	if not staticBoard():
		print("Failed player turn check on second static board check")
		return False
	up()
	if not gunCursorVisible():
		print("Failed player turn  check on second gun cursor check")
		return False
	return True
	
def gunCursorVisible():
	print("Checking for top left of gun cursor cursor")
	topLeft = valueOverAmountInArea(85, 1170, 359, 20, 1)
	print("Checking for bottom right of gun cursor cursor")
	bottomRight = valueOverAmountInArea(85, 1306, 490, 20, 1)
	print(f"Gun cursor top left: {topLeft} top right: {bottomRight}")
	return topLeft and bottomRight

def checkForClearingItems():
	print("## Checking if items are being cleared")
	topLeftItemSectionIsBlack = not valueOverAmountInArea(1, 1306, 490, 30, 30)
	if not topLeftItemSectionIsBlack:
		print("## Items not being cleared. Top left not black.")
		return False
	topRightItemSectionIsBlack = not valueOverAmountInArea(1, 1485, 266, 25, 25)
	if not topRightItemSectionIsBlack:
		print("## Items not being cleared. Top right not black.")
		return False
	bottomLeftItemSectionIsBlack = not valueOverAmountInArea(1, 719, 760, 25, 25)
	if not bottomLeftItemSectionIsBlack:
		print("## Items not being cleared. Bottom left not black.")
		return False
	bottomRightItemSectionIsBlack = not valueOverAmountInArea(1, 1751, 957, 25, 25)
	if not bottomRightItemSectionIsBlack:
		print("## Items not being cleared. Bottom right not black.")
		return False
	centerLineWhite = valueOverAmountInArea(85, 708, 424, 10, 10)
	if not centerLineWhite:
		print("## Items not being cleared. Center line white not found.")
		return False
	bulletSquareWhite = valueOverAmountInArea(85, 1473, 393, 15, 15)
	if not centerLineWhite:
		print("## Items not being cleared. Bullet square white not found.")
		return False
	print("## Found to be clearing items. Hopefully round won triggered.")
	return True

def checkForRoundIsWon() -> bool:
	print("### Checking for round won")
	scoreboardLeftBlack = not valueOverAmountInArea(1, 786, 481, 40, 150)
	if not scoreboardLeftBlack:
		print("### Round not found to be won. scoreboardLeftBlack check failed.")
		return False
	scoreboardRightBlack = not valueOverAmountInArea(1, 1493, 646, 99, 249)
	if not scoreboardRightBlack:
		print("### Round not found to be won. scoreboardRightBlack check failed.")
		return False
	bulletSquareWhite = valueOverAmountInArea(85, 675, 1246, 72, 72)
	if not bulletSquareWhite:
		print("### Round not found to be won. bulletSquareWhite check failed.")
		return False
	dealerItemSquare8White = valueOverAmountInArea(85, 303, 962, 65, 65)
	if not dealerItemSquare8White:
		print("### Round not found to be won. dealerItemSquare8White check failed.")
		return False
	blackAboveScoreboard = not valueOverAmountInArea(1, 615, 120, 31, 69)
	if not blackAboveScoreboard:
		print("### Round not found to be won. blackAboveScoreboard check failed.")
		return False
	ocrText = scoreboardText()
	playerName = getPlayerName()
	if octText == f"{playerName} WINS":
		winRound()
		return True
	return False

def winRound():
	global currentItemPositions
	global roundsCleared
	currentItemPositions.clear()
	roundsCleared += 1
	print("################")
	print(f"## Rounds cleared: {roundsCleared}")
	print("################")
	if roundsCleared == 3:
		print("################")
		print("## Double or Nothing set cleared!")
		print("################")
		#TODO: Choose to begin a new double or nothing set
		roundsCleared = 0
	return 

def hasPlayerLost() -> bool:
	return inStartingBathroom()

def awaitInputs():
	while(True):
		print("# Waiting for player turn")
		while not playerTurn():
			if itemBoxCursorVisible():
				print("# While waiting for the player's turn the item box was found to be open. Grabbing items.")
				grabItems()
				continue
			checkForClearingItems()
			checkForRoundIsWon()
			if hasPlayerLost():
				print("#### Player found to have lost. Returning to bathroom logic.")
				return
			sleep(0.5)
		print("# Should be player turn now.")
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
			usePersonalItem(int(param))
			if extraParam != "":
				print("Extra param given (presumably for adrenaline). Wait for adrenaline usage and movement.")
				sleep(1.5)
				useDealerItem(int(extraParam))
		elif action == 'shoot':
			useGun()
			sleep(0.75)
			if param == 'self':
				chooseSelf()
			elif param == 'dealer':
				chooseDealer()
			else:
				print(f"UNRECOGNIZED TARGET \"{param}\"")
			print("Waiting for shooting animation")
			sleep(2) 
		elif action == 'take':
			grabItems()
		else:
			print(f"UNRECOGNIZED ACTION \"{action}\"")