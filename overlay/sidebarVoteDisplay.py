from typing import Callable, Generic, TypeVar
import logging
import tkinter as tk

#from shared.consts import Target
#from shared.actions import Action, ShootAction, UseItemAction
from bot.vote import Vote, VotingTally, VotingTallyEntry
from .consts import Tags
from .actionVoteDisplay import ActionVoteDisplay

logger = logging.getLogger(__name__)

class SidebarVoteDisplay(ActionVoteDisplay):
	def __init__(self, baseFontSize: int, draw_text_1440: Callable, canvas: tk.Canvas):
		self.baseFontSize = baseFontSize
		self.canvas = canvas
		
		self.initVoteLeaderboards()
	
	def initVoteLeaderboards(self, x1440: int, y1440: int, baseFontSize: int, draw_text_1440: Callable) -> None:
		self.initHeaders(x1440, y1440, baseFontSize, draw_text_1440)
		self.initVoteLists(x1440, y1440, baseFontSize, draw_text_1440)

	def initHeaders(self, x1440: int, y1440: int, baseFontSize: int, draw_text_1440: Callable) -> None:
		pass
	
	def initVoteLists(self, x1440: int, y1440: int, baseFontSize: int, draw_text_1440: Callable) -> None:
		pass