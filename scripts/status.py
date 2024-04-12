from .overlay import getOverlay
from .log import log


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
	log(toPrint)

def status(toPrint: str) -> None:
	global statusStack
	statusStack = [toPrint]
	getOverlay().updateStatusText(toPrint)
	log(toPrint)