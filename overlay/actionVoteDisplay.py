from abc import ABC, abstractmethod
import logging

from .consts import Tags

logger = logging.getLogger(__name__)

class ActionVoteDisplay(ABC):
	
	#TODO: Remove?
	def showActionVoteStatic(self, numbersToDraw: list[int]) -> None:
		logger.debug(f"showActionVoteStatic {numbersToDraw}")
		self.displayItemActionGuides(numbersToDraw)
		
	def clearActionStatic(self) -> None:
		logger.debug("Hiding action static")
		self.canvas.itemconfigure(Tags.ACTION_VOTE_STATIC, state="hidden")
		self.lastDrawnActionNumbers = list[int]()
		
	@abstractmethod
	def displayItemActionGuides(self, numbersToDraw: list[int]) -> None:
		pass