import pyautogui
import focus

def confirm():
	focus.waitFocused()
	print("[CONFIRM]")
	pyautogui.press('enter')

def left():
	focus.waitFocused()
	print("<- LEFT")
	pyautogui.press('left')

def right():
	focus.waitFocused()
	print("-> RIGHT")
	pyautogui.press('right')

def up():
	focus.waitFocused()
	print("^ UP")
	pyautogui.press('up')

def down():
	focus.waitFocused()
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