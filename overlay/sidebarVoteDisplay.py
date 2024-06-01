from typing import Callable, Generic, TypeVar
import logging
import math
import tkinter as tk

from .consts import Tags
from .leaderboard import Leaderboard
from .actionVoteDisplay import ActionVoteDisplay
from shared.consts import getMaxNameLength
from bot.vote import Vote, VotingTally, VotingTallyEntry
from .winningActionReticle import WinningActionReticle

logger = logging.getLogger(__name__)

class SidebarVoteDisplay(Leaderboard, ActionVoteDisplay):
	def __init__(self, baseFontSize: int, draw_text_1440: Callable, canvas: tk.Canvas, winningActionReticle: WinningActionReticle | None):
		self.headerTags = list[str]()
		self.headerTags.append(Tags.ACTION_VOTE_STATIC)
		self.rowTags = list[str]()
		self.rowTags.append(Tags.ACTION_VOTE_STATS)
		self.winningActionReticle: WinningActionReticle | None = winningActionReticle
		
		self.baseFontSize = baseFontSize
		self.draw_text_1440 = draw_text_1440
		self.canvas = canvas
		
		Leaderboard.__init__(self, "Action Votes Ranking", 8, 2540, 20, int(math.ceil(self.baseFontSize*0.85)), self.draw_text_1440, self.canvas, anchor="ne")
		ActionVoteDisplay.__init__(self)

	def getHeaderTags(self) -> list[str]:
		return self.headerTags

	def getBoardRowTags(self) -> list[str]:
		return self.rowTags
	
	def formatRowText(self, tallyEntry: VotingTallyEntry) -> str:
		namePadding = " " * (getMaxNameLength() - len(tallyEntry.getVoteStr()))
		numPadding = " " * (3 - len(str(tallyEntry.getNumVotes()))) #I doubt this bot is ever going to see >999. If it does then it'll screw up the spacing. Oh no. 
		voteStr = f"{tallyEntry.getBaseVoteStr()}{namePadding} {numPadding}[{tallyEntry.getNumVotes()}] ({tallyEntry.getPercentageStr()})"
		logger.debug(f"Formatted leaderboard row:  {voteStr}")
		return voteStr
	
	def drawActionVotes(self, actionVotes: list[VotingTallyEntry], adrenalineItemVotes: list[VotingTallyEntry]) -> None:
		#TODO:  Handle adrenaline votes. Separate leaderboard? Make it a subordinate one?
		sortedAdrenalineVotes: list[VotingTallyEntry] = sorted(adrenalineItemVotes, key = lambda vote: (vote.getNumVotes(), vote.getAdrenalineItemVote()))

		sortedActionVotes: list[VotingTallyEntry] = sorted(actionVotes, key = lambda vote: (vote.getNumVotes(), vote.getBaseVoteStr()))
		sortedActionVotes = sortedActionVotes[: self.maxLen]
		for i in range(len(sortedActionVotes)):
			vote: VotingTallyEntry = sortedActionVotes[i]
			self.canvas.itemconfigure(self.boardRowText[i], text = self.formatRowText(vote))
		
		if self.winningActionReticle is not None:
			self.winningActionReticle.showForList(actionVotes, adrenalineItemVotes)
		
	def displayItemActionGuides(self, numbersToDraw: list[int]) -> None:
		self.showHeader()
		
	def hide(self) -> None:
		super().hide()
		self.winningActionReticle.hide()