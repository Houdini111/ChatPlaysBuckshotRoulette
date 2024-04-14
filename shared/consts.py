from enum import Enum

useNames = ["use", "item", "consume", "take"]
shootNames = ["shoot", "shot", "attack", "hit", "target"]
dealerNames = ["dealer", "them", "guy", "other"]
playerNames = ["self", "me", "player", "i", "myself"]

class ActionEnum(Enum):
	INVALID = -1
	SHOOT = 1
	USE = 2

class Target(Enum):
	INVALID = -1
	SELF = 1
	DEALER = 2
	
def getShootNames():
	return shootNames

def getUseNames():
	return useNames

def getDealerNames():
	return dealerNames

def getPlayerNames():
	return playerNames