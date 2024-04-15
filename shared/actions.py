from abc import ABC, abstractmethod
from typing import Callable

from .consts import Target, getDealerNames, getPlayerNames, getShootNames, getUseNames
from .log import log
from .util import safeInt

#To avoid a circular import, lazy load this method
itemAtPosition: Callable
def setItemAtPositionFunc(func: Callable) -> None:
	global itemAtPosition
	itemAtPosition = func


class Action(ABC):
	@abstractmethod
	def valid() -> bool:
		pass

class ShootAction(Action):
	def __init__(self, target: str | Target):
		self.target: Target
		if type(target) is str:
			self.target = parseTarget(target)
		elif type(target) is Target:
			self.target = target
	
	def getTarget(self) -> Target:
		return self.target

	def valid(self) -> bool:
		return self.target != Target.INVALID
	
	def __str__(self):
		return f"shoot {self.target.value}"

class UseItemAction(Action):
	def __init__(self, itemNum: str | int, adrenalineItemNum: str | int | None = None):
		self.itemNum = safeInt(itemNum, 0)
		#TODO: Check if adrenaline number needed
		self.adrenalineItemNum = safeInt(adrenalineItemNum, 0)
	
	def getItemNum(self) -> int:
		return self.itemNum
	
	def getAdrenalineItemNum(self) -> int:
		return self.adrenalineItemNum
	
	def valid(self) -> bool:
		if not itemAtPosition(self.itemNum):
			return False
		if self.adrenalineItemNum < 0 or self.adrenalineItemNum > 8:
			return False
		return True

#Since python is dumb and won't let me return an instance of the class from a static method belonging to the class, this no longer lives in the Target Enum
def parseTarget(target: str) -> Target:
	target = target.lower()
	if target in getPlayerNames():
		return Target.SELF
	elif target in getDealerNames():
		return Target.DEALER
	log(f"UNRECOGNIZED TARGET: \"{target}\". GIVING INVALID SO INPUT CAN BE IGNORED.")
	return Target.INVALID

def parseAction(userInput: str) -> Action | None:
	userInput = userInput.lower().strip()
	splitInput = userInput.split(' ')
	action = splitInput[0]
	param = ""
	extraParam = ""
	if len(splitInput) > 1:
		param = splitInput[1]
	if len(splitInput) > 2:
		extraParam = splitInput[2]
	if action in getShootNames():
		return ShootAction(param)
	elif action in getUseNames():
		return UseItemAction(param, extraParam)
	else:
		log(f"UNRECOGNIZED ACTION [param, extraParam]: \"{action}\" [\"{param}\", \"{extraParam}\"]")
		return None