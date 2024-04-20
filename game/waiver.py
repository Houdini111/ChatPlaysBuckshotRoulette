import logging
from time import sleep

from .basicActions import up, down, left, right, confirm, anyUse
from overlay.status import status
from bot.chatbot import getChatbot

logger = logging.getLogger(__name__)

playerName = ""
def getPlayerName() -> str:
	return playerName

def waive() -> None:
	global playerName
	pickUpWaiver()
	playerName = getChatbot().getVotedName()
	enterName(playerName)

def pickUpWaiver() -> None:
	status("Picking up waiver")
	anyUse()
	status("Waiting for waiver to be picked up")
	sleep(3.5) #Do I need more? Can I get away with less?

def enterName(name: str) -> None:
	name = name.upper()[0:6] #Normalize to uppercase and truncate to the max of 6 characters
	status(f"Entering name {name}")
	
	logger.debug("In case the player has tabbed out, reactivate cursor by moving off and on")
	right()
	left()

	#cursorOnA() #TODO: Cycles, so I'll have to pixel peep with getpixelcolor to be safer
	#   For now, this works without intervention
	cursorX = 0 
	cursorY = 0
	charMap = {
		'A': [0, 0],
		'B': [1, 0],
		'C': [0, 1],
		'D': [1, 1],
		'E': [2, 1],
		'F': [0, 2],
		'G': [1, 2],
		'H': [0, 3],
		'I': [1, 3],
		'J': [2, 3],
		'K': [3, 3],
		'L': [0, 4],
		'M': [1, 4],
		'N': [2, 4],
		'O': [3, 4],
		'P': [0, 5],
		'Q': [1, 5],
		'R': [2, 5],
		'S': [3, 5],
		'T': [0, 6],
		'U': [1, 6],
		'V': [2, 6],
		'W': [3, 6],
		'X': [0, 7],
		'Y': [1, 7],
		'Z': [2, 7]
	}
	lastChar: str = 'A'
	for char in name:
		if char == lastChar:
			logger.debug(f"Wanting to enter \"{char}\" which is the same as the last one. Just pressing again.")
			confirm()
			continue
		logger.info(f"Attempting to enter char {char}")
		goalX, goalY = charMap[char]
		logger.debug(f"Navigating to char {char}")
		navToChar(cursorX, cursorY, goalX, goalY)
		cursorX = goalX
		cursorY = goalY
		confirm()
		logger.debug(f"Should have entered char {char}")
	submitName(cursorX, cursorY) 
		
def navToChar(startX: int, startY: int, goalX: int, goalY: int) -> None:
	logger.info(f"Navigating to char with positions [{startX}, {startY}] -> [{goalX}, {goalY}]")
	x = startX
	y = startY
	#Avoid traversing columns 3 and 4, as backspace and enter make that unreliable.
	#   Go to at least 2 before going down and then over
	tempGoalX = goalX
	if goalX >= 2:
		tempGoalX = 1
	logger.debug(f"current: [{x}, {y}] goal: [{goalX}, {goalY}] tempGoalX: {tempGoalX}")
	x = navToColumn(x, tempGoalX)
	y = navToRow(y, goalY)
	x = navToColumn(x, goalX)

def navToColumn(current: int, goal: int) -> int:
	while current < goal:
		right()
		current += 1
	while current > goal:
		left()
		current -= 1
	return current

def navToRow(current: int, goal: int) -> int:
	while current < goal:
		down()
		current += 1
	while current > goal:
		up()
		current -= 1
	return current

def submitName(currentX: int, currentY: int) -> None:
	status("Submitting name")
	currentX = navToColumn(currentX, 1)
	currentY = navToRow(currentY, 2)
	currentX = navToColumn(currentX, 2)
	confirm()
	status("Waiting for waiver to be put down")
	sleep(3) #Just enough for the paper to be lowered. The actual wait happens in grabItems