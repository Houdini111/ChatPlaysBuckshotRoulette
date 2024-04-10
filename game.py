from time import sleep
import colorsys
from basicActions import confirm, left, right, up, down, enterDirections, anyUse
from screenColors import getPixelAreaAverageBy1440p, getPixelAreaBy1440p, pixelsMatch, valueOverAmountInArea



currentItemPositions = []




#TODO: 
#  Handle dialogue box (currently registers as being player turn)
#  Item place logic not skipping squares
#  Sometimes endless activations goes to leaderboards instead

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
	'''
	#Targeting the dark shadow on the left of the box
	areaColor = getPixelAreaAverageBy1440p(1025, 467, 10, 10)
	r, g, b = areaColor
	#I have yet to see this anything other than true black, but add a bit of wiggle room in case
	return r < 5 and g < 5 and b < 5
	'''
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
	#sleep(1) #Sleep for a little extra because of the interactive delay
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
	#print("All items withdrawn. Waiting for loading animation.")
	#sleep(12) #Maximum wait time assumes 8 shells to loading

'''
def dealerPixels():
	return getPixelAreaAverageBy1440p(1248, 505, 28, 28)

def dealerSeen():
	#This logic relies on the fact that the dealer's head bobs, thus changing the pixels in this zone
	#   Meanwhile, the player's board is completely static
	r1, g1, b1 = dealerPixels()
	sleep(0.1)
	t2, g2, b2 = dealerPixels()
	return r1 != r2 and g1 != g2 and b1 != b2

def pixelsDifferent(old, new):
	return old[0] != new[0] or old[1] != new[1] or old[2] != new[2]

def playerTurn():
	#There are several second pauses during actions (like when he disappears into the void after being shot)
	#   As such, check to see if the dealer (who moves) can be seen. 
	#   And keep checking until he can't be seen for multiple checks in a row. 
	dealerPixelHistory = []
	newPixels = dealerPixels()
	dealerPixelHistory.append(newPixels)
	sleep(0.1)
	while (True): #TODO: Find exit condition
		oldPixels = dealerPixelHistory[-1]
		newPixels = dealerPixels()
		dealerPixelHistory.append(newPixels)
		
		changed = pixelsDifferent(oldPixels, newPixels)
	
	if dealerSeen():
		print("Waiting for dealer to not be seen)
	while dealerSeen():
		sleep(4)
	sleep(4) #Wait for four seconds to 
'''		

########### TODO: Maybe just check for specific gun pixels? Have to save them from the first time after the item pickup and load
###########       Or maybe just spam up and wait for the cursor to show up

'''
staticFramePixels = []
nonboxStaticFramePixels = []
def playerTurn():
	#print(f"Static pixels first order len: {len(staticFramePixels)}")
	currentPixels = getGunPixels()
	return pixelsMatch(staticFramePixels, currentPixels)

def saveGunPixels():
	global staticFramePixels
	staticFramePixels = getGunPixels()
	print(f"Saved static pixels to find player turn. First order len: {len(staticFramePixels)}")

def getGunPixels():
	return getPixelAreaBy1440p(1373, 1416, 24, 24) #Bottom edge of table

def boxNotVisible():
	currentPixels = getNonBoxPixels()
	return pixelsMatch(nonboxStaticFramePixels, currentPixels)

def saveNonBoxPixels():
	global nonboxStaticFramePixels
	nonboxStaticFramePixels = getNonBoxPixels()
	print(f"Saved non-box pixels to find if it's box time. First order len: {len(nonboxStaticFramePixels)}")

def getNonBoxPixels():
	return getPixelAreaBy1440p(1445, 674, 21, 21) #Top right of item box square

def savePixels():
	saveGunPixels()
	saveNonBoxPixels()
'''
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

def awaitInputs():
	while(True):
		print("# Waiting for player turn")
		while not playerTurn() and not itemBoxCursorVisible():
			sleep(0.5)
		print("# Either playerTrn or itemBoxCursorVisible")
		if itemBoxCursorVisible():
			grabItems()
			continue
		#print("Is player turn? Wait then check for static non-box pixels")
		#if not boxNotVisible():
		#	print("Item box found?. Grab items.")
		#	grabItems()
		#print("Item box should be done? Seems to actually be player turn now")
	
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
				sleep(2.5)
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