from time import sleep
from basicActions import confirm, up, enterDirections
from items import grabItems, itemBoxCursorVisible
from screenColors import valueOverAmountInArea
from waiver import getPlayerName
from image import scoreboardText
from bathroom import inStartingBathroom



roundsCleared = 0




#TODO: 
#  Item place logic sometimes skipping squares
#  Sometimes activating endless goes to leaderboards instead


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
	if ocrText == f"{playerName} WINS":
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
		while (True):
			request = input("Next? ")
			if doAction(request):
				break