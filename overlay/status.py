import inspect
from logging import Logger
import logging
from types import FrameType, ModuleType
from typing import Any

from .overlay import getOverlay

fallbackLogger = logging.getLogger(__name__)

statusStack = []
def removeTempStatus() -> None:
	global statusStack
	statusStack.pop()
	status = ""
	if len(statusStack) > 0:
		status = statusStack[-1]
	getOverlay().updateStatusText(status)

def removeAllTempStatus() -> None:
	global statusStack
	while len(statusStack) > 1:
		statusStack.pop()
	status = ""
	if len(statusStack) > 0:
		status = statusStack[-1]
	getOverlay().updateStatusText(status)

def tempStatus(toPrint: str) -> None:
	global statusStack
	statusStack.append(toPrint)
	getOverlay().updateStatusText(toPrint)
	callerLog(toPrint)

def status(toPrint: str) -> None:
	global statusStack
	statusStack = [toPrint]
	getOverlay().updateStatusText(toPrint)
	callerLog(toPrint)
	

def callerLog(logLine: str) -> None:
	getLogger().info(logLine)

def getLogger() -> Logger:
	logger: Logger | None = getCallerLogger()
	if logger is None:
		fallbackLogger.warn("Failed to get caller's logger for stack trace", stack_info=True)
		return fallbackLogger
	return logger

def getCallerLogger() -> Logger | None:
	module: ModuleType | None = callers_module()
	if module is None:
		return None
	for (name, value) in inspect.getmembers(module):
		if name == "logger":
			if type(value) is not Logger:
				fallbackLogger.warn(f"Found logger for module {module.__name__} but was not of type Logger. Instead was {type(value)}")
				return None
			return value
	fallbackLogger.warn(f"Could not find logger for module: {module.__name__}")
	return None

#Modified based on https://stackoverflow.com/a/2001032
def callers_module() -> ModuleType | None:
	currentFrame: FrameType | None = inspect.currentframe()
	while currentFrame is not None:
		currentFrameModule = inspect.getmodule(currentFrame.f_back)
		if currentFrameModule.__name__ == __name__: #Still in this module. Keep going backwards
			currentFrame = currentFrame.f_back
		else: #Reached a new module, return this first new module
			return currentFrameModule
	return None