import pyautogui
from focus import waitFocused

def confirm():
	waitFocused()
	print("[CONFIRM]")
	pyautogui.press('enter')

def left():
	waitFocused()
	print("<- LEFT")
	pyautogui.press('left')

def right():
	waitFocused()
	print("-> RIGHT")
	pyautogui.press('right')

def up():
	waitFocused()
	print("^ UP")
	pyautogui.press('up')

def down():
	waitFocused()
	print("v DOWN")
	pyautogui.press('down')
	
def enterDirections(directions):
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