import pyautogui
from focus import waitForFocus

def confirm():
	waitForFocus()
	print("[CONFIRM]")
	pyautogui.press('enter')

def left():
	waitForFocus()
	print("<- LEFT")
	pyautogui.press('left')

def right():
	waitForFocus()
	print("-> RIGHT")
	pyautogui.press('right')

def up():
	waitForFocus()
	print("^ UP")
	pyautogui.press('up')

def down():
	waitForFocus()
	print("v DOWN")
	pyautogui.press('down')
	
def enterDirections(directions):
	print(f"Entering directions {directions}")
	if directions is None or len(directions) == 0:
		return
	for dir in directions:
		if dir == 'l':
			left()
		elif dir == 'r':
			right()
		elif dir == 'u':
			up()
		elif dir == 'd':
			down()
		else:
			print(f"Unrecognized direction: [{dir}]")
			
def anyUse():
	print("### Any use")
	left() #Any key
	confirm()