import logging

from .leaderboard2 import Leaderboard
from shared.consts import getMaxNameLength
from bot.vote import VotingTallyEntry

logger = logging.getLogger(__name__)

class NameLeaderboard(Leaderboard):
	def formatRowText(self, tallyEntry: VotingTallyEntry) -> str:
		namePadding = " " * (getMaxNameLength() - len(tallyEntry.getVoteStr()))
		numPadding = " " * (3 - len(str(tallyEntry.getNumVotes()))) #I doubt this bot is ever going to see >999. If it does then it'll screw up the spacing. Oh no. 
		voteStr = f"{tallyEntry.getVoteStr()}{namePadding} {numPadding}[{tallyEntry.getNumVotes()}] ({tallyEntry.getPercentageStr()})"
		logger.debug(f"Formatted leaderboard row:  {voteStr}")
		return voteStr