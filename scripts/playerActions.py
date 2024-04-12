from abc import ABC, abstractmethod
from enum import Enum
from time import sleep

from .items import itemAtPosition, getPlayerItemDirections, getDealerItemDirections, removeItem
from .util import safeInt
from .basicActions import up, down, confirm, enterDirections
from .log import log
from .status import status

class Target(Enum):
	INVALID = -1
	SELF = 1
	DEALER = 2

#Since python is dumb and won't let me return an instance of the class from a static method belonging to the class, this no longer lives in the Target Enum
def parseTarget(target: str) -> Target:
	target = target.lower()
	if target == "self" or target == "player" or target == "me":
		return Target.SELF
	elif target == "dealer" or target == "them" or target == "him" :
		return Target.DEALER
	log(f"UNRECOGNIZED TARGET: \"{target}\". GIVING INVALID SO INPUT CAN BE IGNORED.")
	return Target.INVALID

class Action(ABC):
	@abstractmethod
	def execute() -> bool:
		pass
	
	@abstractmethod
	def valid() -> bool:
		pass

class ShootAction(Action):
	def __init__(self, target: str | Target):
		if type(target) is str:
			target = parseTarget(target)
		self.target = target
	
	def valid(self) -> bool:
		return self.target != Target.INVALID

	def execute(self) -> bool:
		if not self.valid():
			return False

		status("Executing shoot action")
		useGun()
		sleep(0.75) #Wait for gun move animation
		if self.target == Target.SELF:
			chooseSelf()
		elif self.target == Target.DEALER:
			chooseDealer()
		return True

class UseItemAction(Action):
	def __init__(self, itemNum: str | int, adrenalineItemNum: str | int | None = None):
		self.itemNum = safeInt(itemNum, 0)
		#TODO: Check if adrenaline number needed
		self.adrenalineItemNum = safeInt(adrenalineItemNum, 0)
		pass
	
	def valid(self) -> bool:
		if not itemAtPosition(self.itemNum):
			return False
		if self.adrenalineItemNum < 0 or self.adrenalineItemNum > 8:
			return False
		return True
	
	def execute(self) -> bool:
		if not self.valid():
			return False
		
		status("Executing use item action")
		#TODO: Check if dealer has item at location (difficult because I have to do pixel peeping that can vary based on the item it is and the item possibly in front)
		usePersonalItem(self.itemNum)
		if self.adrenalineItemNum != 0:
			log("Extra param given (presumably for adrenaline). Wait for adrenaline usage and movement.")
			sleep(1.5)
			useDealerItem(self.adrenalineItemNum)
		return True

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
	if action == 'shoot' or action == 'shot' or action == 'gun' or action == 'shotgun':
		return ShootAction(param)
	elif action == 'use' or action == 'item' or action == 'consume':
		return UseItemAction(param, extraParam)
	else:
		log(f"UNRECOGNIZED ACTION [param, extraParam]: \"{action}\" [\"{param}\", \"{extraParam}\"]")
		return None



def cursorGun():
	up()
	up()
	
def cursorItem(num):
	cursorGun()
	enterDirections(getPlayerItemDirections(num, "use"))

def useGun():
	cursorGun()
	confirm()

def usePersonalItem(num):
	global currentItemPositions
	cursorItem(num)
	confirm()
	removeItem(num)
	status("Waiting for item use animation")
	#Is there a good way to check for which item it is to only wait as long as needed? 
	#This long of a wait might conflict with adrenaline
	sleep(6) #Has to be extra long for phone. 
	log("Item use animation should be over")

def useDealerItem(num):
	down() #Move to ensure cursor is active
	enterDirections(getDealerItemDirections(num))
	confirm()
	
def chooseDealer():
	up()
	confirm()

def chooseSelf():
	down()
	confirm()