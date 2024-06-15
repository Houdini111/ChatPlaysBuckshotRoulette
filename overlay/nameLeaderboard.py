import logging
from typing import Callable
import tkinter as tk

from .leaderboard import Leaderboard
from .consts import Tags
from shared.consts import getMaxNameLength
from bot.vote import VotingTallyEntry

logger = logging.getLogger(__name__)

class NameLeaderboard(Leaderboard):
	def __init__(self, header: str, maxLen: int, x1440: int, y1440: int, baseFontSize: int, draw_text_1440: Callable, canvas: tk.Canvas, anchor: str = "nw") -> None:
		self.headerTags = list[str]()
		self.headerTags.append(Tags.NAME_LEADERBOARD_HEADER)
		self.rowTags = list[str]()
		self.rowTags.append(Tags.NAME_LEADERBOARD_ENTRY)
		super().__init__(header, maxLen, x1440, y1440, baseFontSize, draw_text_1440, canvas, anchor)

	def getHeaderTags(self) -> list[str]:
		return self.headerTags

	def getBoardRowTags(self) -> list[str]:
		return self.rowTags

	def formatRowText(self, tallyEntry: VotingTallyEntry) -> str:
		namePadding = " " * (getMaxNameLength() - len(tallyEntry.getVoteStr()))
		numPadding = " " * (3 - len(str(tallyEntry.getNumVotes()))) #I doubt this bot is ever going to see >999. If it does then it'll screw up the spacing. Oh no. 
		voteStr = f"{tallyEntry.getVoteStr()}{namePadding} {numPadding}[{tallyEntry.getNumVotes()}] ({tallyEntry.getPercentageStr()})"
		logger.debug(f"Formatted leaderboard row:  {voteStr}")
		return voteStr