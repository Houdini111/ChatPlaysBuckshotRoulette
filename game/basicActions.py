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
	
def enterDirections(*directions: list[str] | str) -> None:
	logger.info(f"Entering directions {directions}")
	combined = list[str]()
	for direction in directions:
		dirType: type = type(direction)
		logger.debug(f"Direction {direction} in provided list of directions is of type {dirType}")
		if dirType is str:
			combined.append(direction)
		elif dirType is list or dirType is tuple:
			combined.extend(direction)
	logger.debug(f"Combined list of requested directions: {combined}")
	if len(combined) == 0:
		return
	for inDir in combined:
		inDir = inDir.lower()
		if inDir in ('l', 'left'):
			left()
		elif inDir in ('r', 'right'):
			right()
		elif inDir in ('u', 'up'):
			up()
		elif inDir in ('d', 'down'):
			down()
		else:
			logger.info(f"Unrecognized direction: [{dir}]")
			
def anyUse() -> None:
	logger.info("Any use")
	left() #Any key
	confirm()