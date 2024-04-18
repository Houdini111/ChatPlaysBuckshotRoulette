import asyncio
import logging
import threading
from time import sleep
from typing import Callable
import math
import pyautogui

from .consts import ActionEnum, Target, getDealerNames, getPlayerNames, getShootNames

logger = logging.getLogger(__name__)

class Rectangle():
	def __init__(self, x: int, y: int, w: int, h: int):
		self.x = x
		self.y = y
		self.w = w
		self.h = h
	
	def __str__(self) -> str:
		return "{" + f"x: {self.x}, y: {self.y}, w: {self.w}, y: {self.h}" + "}"

def waitForFalse(checker: Callable[[], bool]) -> None:
	logger.info("Waiting for method to return false")
	i = 0
	while checker():
		i += 1
		logger.debug(f"Waiting for method to return false. Attempts: {i}")
		sleep(0.1)

def waitForTrue(checker: Callable[[], bool]) -> None:
	logger.info("Waiting for method to return true")
	i = 0
	while not checker():
		i += 1
		logger.debug(f"Waiting for method to return true. Attempts: {i}")
		sleep(0.1)

def resizeXFrom1440p(x1440: int) -> int:
	xPercent = x1440/2560
	displayW, displayH = pyautogui.size()
	return int(math.ceil(xPercent * displayW))

def resizeYFrom1440p(y1440: int) -> int:
	yPercent = y1440/1440
	displayW, displayH = pyautogui.size()
	return int(math.ceil(yPercent * displayH))
	
def safeInt(inVal: str | int | None, defaultValue: int) -> int:
	if type(inVal) is int:
		return inVal
	elif type(inVal) is str and inVal.isdigit():
		return int(inVal)
	return defaultValue

def resizePointFrom1440p(x1440: int, y1440: int) -> list[int]:
	return [resizeXFrom1440p(x1440), resizeYFrom1440p(y1440)]

def resizeRectFrom1440p(x1440: int, y1440: int, w1440: int, h1440: int) -> list[int]:
	wPercent = w1440/2560
	hPercent = h1440/1440
	displayW, displayH = pyautogui.size()
	realW = int(math.ceil(wPercent * displayW))
	realH = int(math.ceil(hPercent * displayH))
	realX, realY = resizePointFrom1440p(x1440, y1440)
	return [realX, realY, realW, realH]

#This method from https://stackoverflow.com/a/61331974
def run_task(coroutine: Callable):
	try:
		loop = asyncio.get_running_loop()
	except RuntimeError:  # 'RuntimeError: There is no current event loop...'
		loop = None

	if loop and loop.is_running():
		logger.debug('Async event loop already running. Adding coroutine to the event loop.')
		tsk = loop.create_task(coroutine())
		# ^-- https://docs.python.org/3/library/asyncio-task.html#task-object
		# Optionally, a callback function can be executed when the coroutine completes
		tsk.add_done_callback(
			lambda t: print(f'Task done with result={t.result()}  << return val of coroutine()'))
	else:
		logger.debug('Starting new event loop')
		result = asyncio.run(coroutine())