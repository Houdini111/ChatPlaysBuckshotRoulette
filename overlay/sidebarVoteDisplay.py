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

def formatRowText(tallyEntry: VotingTallyEntry, namePaddingLength: int = getMaxNameLength()) -> str:
	missingNameLen: int = namePaddingLength - len(tallyEntry.getVoteStr())
	namePadding: str = " " * missingNameLen
	numVotesLen: int = len(str(tallyEntry.getNumVotes()))
	missingVoteLen: int = 3 - numVotesLen #I doubt this bot is ever going to see >999. If it does then it'll screw up the spacing. Oh no. 
	numPadding: str = " " * missingVoteLen 
	voteStr: str = f"{tallyEntry.getBaseVoteStr()}{namePadding} {numPadding}[{tallyEntry.getNumVotes()}] ({tallyEntry.getPercentageStr()})"
	logger.debug(f"Formatted leaderboard row:  {voteStr}")
	return voteStr


class ActionLeaderboard(Leaderboard):
	def __init__(self, baseFontSize: int, draw_text_1440: Callable, canvas: tk.Canvas):
		self.headerTags = list[str]()
		self.headerTags.append(Tags.ACTION_VOTE_STATIC)
		self.headerTags.append(Tags.SIDEBAR_ACTION_HEADER)
		self.rowTags = list[str]()
		self.rowTags.append(Tags.ACTION_VOTE_STATS)
		self.rowTags.append(Tags.SIDEBAR_ACTION_ENTRY)
		self.maxLen = 8 #Make configurable?
		super().__init__("Action Votes Ranking", self.maxLen, 2540, 20, baseFontSize, draw_text_1440, canvas, anchor="ne")

	def getHeaderTags(self) -> list[str]:
		return self.headerTags

	def getBoardRowTags(self) -> list[str]:
		return self.rowTags
	
	def formatRowText(self, tallyEntry: VotingTallyEntry) -> str:
		return formatRowText(tallyEntry)
	
class AdrenalineLeaderboard(Leaderboard):
	def __init__(self, baseFontSize: int, draw_text_1440: Callable, canvas: tk.Canvas):
		self.headerTags = list[str]()
		self.headerTags.append(Tags.ACTION_VOTE_STATIC)
		self.headerTags.append(Tags.SIDEBAR_ADRENALINE_HEADER)
		self.rowTags = list[str]()
		self.rowTags.append(Tags.ACTION_VOTE_STATS)
		self.rowTags.append(Tags.SIDEBAR_ADRENALINE_ENTRY)
		self.maxLen = 8 #Make configurable?
		super().__init__("Adrenaline Votes Ranking", self.maxLen, 2540, (1440/2)+20, baseFontSize, draw_text_1440, canvas, anchor="ne")

	def getHeaderTags(self) -> list[str]:
		return self.headerTags

	def getBoardRowTags(self) -> list[str]:
		return self.rowTags

	def formatRowText(self, tallyEntry: VotingTallyEntry) -> str:
		return formatRowText(tallyEntry, 1)

class SidebarVoteDisplay(ActionVoteDisplay):
	def __init__(self, baseFontSize: int, draw_text_1440: Callable, canvas: tk.Canvas, winningActionReticle: WinningActionReticle | None):
		self.headerTags = list[str]()
		self.headerTags.append(Tags.ACTION_VOTE_STATIC)
		self.rowTags = list[str]()
		self.rowTags.append(Tags.ACTION_VOTE_STATS)
		self.winningActionReticle: WinningActionReticle | None = winningActionReticle
		
		self.baseFontSize = baseFontSize
		self.draw_text_1440 = draw_text_1440
		self.canvas = canvas
		
		self.maxLen = 8 #Make configurable?
		
		self.actionVoteLeaderboard = ActionLeaderboard(int(math.ceil(self.baseFontSize*0.85)), self.draw_text_1440, self.canvas)
		self.adrenalineVoteLeaderboard = AdrenalineLeaderboard(int(math.ceil(self.baseFontSize*0.85)), self.draw_text_1440, self.canvas)
		ActionVoteDisplay.__init__(self)
	
	def drawActionVotes(self, actionVotes: list[VotingTallyEntry], adrenalineItemVotes: list[VotingTallyEntry]) -> None:
		logger.debug(f"SidebarVoteDisplay displaying {len(actionVotes)} actions and {len(adrenalineItemVotes)} adrenaline items")
		sortedAdrenalineVotes: list[VotingTallyEntry] = sorted(adrenalineItemVotes, key = lambda vote: (vote.getNumVotes(), vote.getAdrenalineItemVote()))

		sortedActionVotes: list[VotingTallyEntry] = sorted(actionVotes, key = lambda vote: (vote.getNumVotes(), vote.getBaseVoteStr()))
		sortedActionVotes = sortedActionVotes[: self.maxLen]
		self.actionVoteLeaderboard.displayVotes(sortedActionVotes)
		
		filteredAdrenalineVotes: list[VotingTallyEntry] = filter(lambda vote: vote.getNumVotes() > 0, adrenalineItemVotes)
		sortedAdrenalineVotes: list[VotingTallyEntry] = sorted(filteredAdrenalineVotes, key = lambda vote: (vote.getNumVotes(), vote.getBaseVoteStr()))
		sortedAdrenalineVotes = sortedAdrenalineVotes[: self.maxLen]
		self.adrenalineVoteLeaderboard.displayVotes(sortedAdrenalineVotes)

		if self.winningActionReticle is not None:
			self.winningActionReticle.showForList(actionVotes, adrenalineItemVotes)
		
	def displayItemActionGuides(self, numbersToDraw: list[int]) -> None:
		logger.debug(f"SidebarVoteDisplay displaying headers (also nominally showing action guides for numbers {numbersToDraw})")
		self.actionVoteLeaderboard.showHeader()
		self.adrenalineVoteLeaderboard.showHeader()
		
	def hide(self) -> None:
		logger.debug("SidebarVoteDisplay hiding all of self")
		self.actionVoteLeaderboard.hide()
		self.adrenalineVoteLeaderboard.hide()
		self.winningActionReticle.hide()