import pyautogui
from focus import waitForFocus

def confirm() -> None:
	waitForFocus()
	print("[CONFIRM]")
	pyautogui.press('enter')

def left() -> None:
	waitForFocus()
	print("<- LEFT")
	pyautogui.press('left')

def right() -> None:
	waitForFocus()
	print("-> RIGHT")
	pyautogui.press('right')

def up() -> None:
	waitForFocus()
	print("^ UP")
	pyautogui.press('up')

def down() -> None:
	waitForFocus()
	print("v DOWN")
	pyautogui.press('down')
	
def enterDirections(directions: list[str]) -> None:
	print(f"Entering directions {directions}")
	if len(directions) == 0:
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
			
def anyUse() -> None:
	print("### Any use")
	left() #Any key
	confirm()