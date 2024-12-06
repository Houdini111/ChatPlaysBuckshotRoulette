from abc import ABC, abstractmethod
import logging

from .consts import Tags
from bot.vote import VotingTallyEntry

logger = logging.getLogger(__name__)

class ActionVoteDisplay(ABC):
	@abstractmethod
	def drawActionVotes(self, actionVotes: list[VotingTallyEntry], adrenalineItemVotes: list[VotingTallyEntry]) -> None:
		pass

	@abstractmethod
	def displayStaticElements(self, numbersToDraw: list[int]) -> None:
		pass
	
	@abstractmethod
	def clearActionVotes(self) -> None:
		pass
	
	@abstractmethod
	def clearStaticElements(self) -> None:
		pass