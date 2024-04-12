import pyautogui

from .focus import waitForFocus
from .log import log

def confirm() -> None:
	waitForFocus()
	log("[CONFIRM]")
	pyautogui.press('enter')

def left() -> None:
	waitForFocus()
	log("<- LEFT")
	pyautogui.press('left')

def right() -> None:
	waitForFocus()
	log("-> RIGHT")
	pyautogui.press('right')

def up() -> None:
	waitForFocus()
	log("^ UP")
	pyautogui.press('up')

def down() -> None:
	waitForFocus()
	log("v DOWN")
	pyautogui.press('down')
	
def enterDirections(directions: list[str]) -> None:
	log(f"Entering directions {directions}")
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
			log(f"Unrecognized direction: [{dir}]")
			
def anyUse() -> None:
	log("Any use")
	left() #Any key
	confirm()