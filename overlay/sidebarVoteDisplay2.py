import logging

from .leaderboard2 import Leaderboard
from .actionVoteDisplay2 import ActionVoteDisplay
from shared.actions import Action, ShootAction
from shared.consts import getMaxNameLength, Target
from bot.vote import VotingTallyEntry, Vote

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
	@staticmethod
	def sampleLargestText():
		fakeVote: Vote = Vote[Action](ShootAction(Target.DEALER), 999)
		fakeTallyEntry: VotingTallyEntry = VotingTallyEntry(fakeVote, 999)
		return formatRowText(fakeTallyEntry)

	def formatRowText(self, tallyEntry: VotingTallyEntry) -> str:
		return formatRowText(tallyEntry)
	
class AdrenalineLeaderboard(Leaderboard):
	@staticmethod
	def sampleLargestText():
		fakeVote: Vote = Vote[str]("1", 999)
		fakeTallyEntry: VotingTallyEntry = VotingTallyEntry(fakeVote, 999)
		return formatRowText(fakeTallyEntry)
	
	def formatRowText(self, tallyEntry: VotingTallyEntry) -> str:
		return formatRowText(tallyEntry)
	
class SidebarVoteDisplay(ActionVoteDisplay):
	def __init__(self, actionLeaderboard: ActionLeaderboard, adrenalineLeaderboard: AdrenalineLeaderboard):
		logger.debug("SidebarVoteDisplay2 created")
		self.actionLeaderboard = actionLeaderboard
		self.adrenalineLeaderboard = adrenalineLeaderboard

	def drawActionVotes(self, actionVotes: list[VotingTallyEntry], adrenalineItemVotes: list[VotingTallyEntry]) -> None:
		logger.debug("SidebarVoteDisplay2 drawing action votes")
		self.actionLeaderboard.displayVotes(actionVotes)
		clearedAdrenalineItemVotes: list[VotingTallyEntry] = list()
		for adrenalineItemVote in adrenalineItemVotes:
			if adrenalineItemVote.getNumVotes() != 0:
				clearedAdrenalineItemVotes.append(adrenalineItemVote)
		self.adrenalineLeaderboard.displayVotes(clearedAdrenalineItemVotes)

	def displayStaticElements(self, numbersToDraw: list[int]) -> None:
		logger.debug("SidebarVoteDisplay2 displaying static elements")
		#numbersToDraw parameter is ignored because this doesn't display any
		self.clearActionVotes()
		self.actionLeaderboard.show()
		self.adrenalineLeaderboard.show()
	
	def clearActionVotes(self) -> None:
		logger.debug("SidebarVoteDisplay2 clearing votes")
		self.actionLeaderboard.clearRows()
		self.adrenalineLeaderboard.clearRows()
	
	def clearStaticElements(self) -> None:
		logger.debug("SidebarVoteDisplay2 clearing static elements")
		self.actionLeaderboard.hide()
		self.adrenalineLeaderboard.hide()