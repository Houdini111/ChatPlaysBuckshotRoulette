from enum import Enum
import logging

logging.getLogger(__name__)

useNames = ["use", "item", "consume", "take"]
shootNames = ["shoot", "shot", "attack", "hit", "target"]
dealerNames = ["dealer", "them", "guy", "other"]
playerNames = ["self", "me", "player", "i", "myself"]

maxNameLength: int = 6
nameLeaderboardCount: int = 5

class StrEnum(Enum):
	def __str__(self):
		return self.value

class ActionEnum(StrEnum):
	INVALID = "INVALID"
	SHOOT = "Shoot"
	USE = "Use"

class Target(StrEnum):
	INVALID = "INVALID"
	SELF = "Player"
	DEALER = "Dealer"
	
def getShootNames():
	return shootNames

def getUseNames():
	return useNames

def getDealerNames():
	return dealerNames

def getPlayerNames():
	return playerNames

def getMaxNameLength():
	return maxNameLength