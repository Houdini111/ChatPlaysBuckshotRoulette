from time import sleep
from basicActions import confirm, left, right, up, down, enterDirections, anyUse

def waive(name: str):
	pickUpWaiver()
	enterName(name)

def pickUpWaiver():
	print("##### Picking up waiver")
	anyUse()
	sleep(4) #Do I need more? Can I get away with less?

def enterName(name: str):
	name = name.upper()[0:6] #Normalize to uppercase and truncate to the max of 6 characters
	print("##### Entering name", name)
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
	for char in name:
		print("Attempting to enter char", char)
		if char == 'A' and cursorX == 0 and cursorY == 0:
			print("### Navigating to char A (Special case)")
			#Because char A is the starting, and the entering only works if there is a cursor
			#  We need to move it off and back on to ensure it's selected
			right()
			left()
			confirm()
		else:
			goalX, goalY = charMap[char]
			print("### Navigating to char", char)
			navToChar(cursorX, cursorY, goalX, goalY)
			cursorX = goalX
			cursorY = goalY
			confirm()
		print("### Should have entered char", char)
	submitName(cursorX, cursorY) 
		
def navToChar(startX, startY, goalX, goalY):
	x = startX
	y = startY
	#Avoid traversing columns 3 and 4, as backspace and enter make that unreliable.
	#   Go to at least 2 before going down and then over
	tempGoalX = goalX
	if goalX >= 3:
		tempGoalX = 2
	#print(f"current: [{x}, {y}] goal: [{goalX}, {goalY}] tempGoalX: {tempGoalX}")
	x = navToColumn(x, tempGoalX)
	y = navToRow(y, goalY)
	x = navToColumn(x, goalX)

def navToColumn(current, goal):
	while current < goal:
		right()
		current += 1
	while current > goal:
		left()
		current -= 1
	return current

def navToRow(current, goal):
	while current < goal:
		down()
		current += 1
	while current > goal:
		up()
		current -= 1
	return current

def submitName(currentX, currentY):
	print("##### Submitting name")
	currentX = navToColumn(currentX, 1)
	currentY = navToRow(currentY, 2)
	currentX = navToColumn(currentX, 2)
	confirm()
	sleep(3) #Just enough for the paper to be lowered. The actual wait happens in grabItems