from abc import ABC, abstractmethod

from bot.vote import VotingTallyEntry

class Overlay(ABC):
	@abstractmethod
	def start(self):
		pass
	
	@abstractmethod
	def stop(self):
		pass

	@abstractmethod
	def updateStatusText(self, text: str) -> None:
		pass
	
	@abstractmethod
	def clearOldNameLeaderboard(self) -> None:
		pass
	
	@abstractmethod
	def drawNameVoteLeaderboard(self, votes: list[VotingTallyEntry]) -> None:
		pass
		
	@abstractmethod
	def displayItemActionGuides(self, numbersToDraw: list[int]) -> None:
		pass
		
	@abstractmethod
	def drawActionVotes(self, actionVotes: list[VotingTallyEntry], adrenalineItemVotes: list[VotingTallyEntry]) -> None:
		pass
		
	@abstractmethod	
	def clearActionOverlay(self) -> None:
		pass
		
	@abstractmethod
	def clearActionVoteStatic(self) -> None:
		pass
		
	@abstractmethod
	def clearActionVotes(self) -> None:
		pass
		
	@abstractmethod
	def hideActionReticle(self) -> None:
		pass
	
overlay: Overlay
def setOverlayToThis(newOverlay: Overlay) -> None:
	global overlay
	overlay = newOverlay
	print("")

def getOverlay() -> Overlay:
	return overlay