import logging
import pyautogui

from .focus import waitForFocus

logger = logging.getLogger(__name__)

def confirm() -> None:
	waitForFocus()
	logger.info("[CONFIRM]")
	pyautogui.press('enter')

def left() -> None:
	waitForFocus()
	logger.info("<- LEFT")
	pyautogui.press('left')

def right() -> None:
	waitForFocus()
	logger.info("-> RIGHT")
	pyautogui.press('right')

def up() -> None:
	waitForFocus()
	logger.info("^ UP")
	pyautogui.press('up')

def down() -> None:
	waitForFocus()
	logger.info("v DOWN")
	pyautogui.press('down')
	
def enterDirections(directions: list[str]) -> None:
	logger.info(f"Entering directions {directions}")
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
			logger.info(f"Unrecognized direction: [{dir}]")
			
def anyUse() -> None:
	logger.info("Any use")
	left() #Any key
	confirm()