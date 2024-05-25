import logging
import random
from typing import Generic, Iterator, OrderedDict, TypeVar, Type
from copy import deepcopy

from shared.actions import Action

logger = logging.getLogger(__name__)

VoteType = TypeVar("VoteType", str, Action)

class Vote(Generic[VoteType]): 
	def __init__(self, vote: VoteType, numVotes: int, isAdrenalineItem: bool = False):
		self.voteType: Type[VoteType] = type(vote)
		self.vote: VoteType = vote
		self.numVotes = numVotes
		self._isAdrenalineItem = isAdrenalineItem
	
	def __lt__(self, other):
		return self.numVotes < other.numVotes
	
	def __copy__(self):
		return deepcopy(self)
	
	def __deepcopy__(self, memo):
		ret = Vote(self.vote, self.numVotes, self.isAdrenalineItem)
		memo[id(self)] = ret
		return ret
	
	def __str__(self):
		return "Vote{vote:\"" + str(self.vote) + "\", numVotes: " + str(self.numVotes) + ", isAdrenalineItem: " + str(self._isAdrenalineItem) + "}"
	
	def __eq__(self, other):
		return str(self.vote) == str(other)
	
	def getVote(self) -> VoteType:
		logger.debug(f"Vote's vote: [{self.vote}]")
		return self.vote
	
	def getNumVotes(self) -> int:
		return self.numVotes
	
	def addAVote(self) -> int:
		self.numVotes += 1
		return self.numVotes
	
	def removeAVote(self) -> int:
		self.numVotes -= 1
		return self.numVotes
	
	def isAdrenalineItem(self) -> bool:
		return self._isAdrenalineItem


class RunningVote(Generic[VoteType]):
	def __init__(self, votes: list[Vote[VoteType]] | None = None, dealerItemVotes: list[int] | None = None):
		self.voteType: TypeVar = VoteType
		self.votes: OrderedDict[str, Vote[VoteType]] = OrderedDict()
		self.dealerItemVotes: list[int] = list[int]()
		for i in range(8):
			self.dealerItemVotes.append(0)
		self.totalVotes = 0
		self.sorted = True

		if votes is not None:
			self.sorted = False
			for vote in votes:
				self.totalVotes += vote.getNumVotes()
			for vote in votes:
				self.votes[str(vote.getVote())] = vote
		self.sort()	
		
	def __copy__(self):
		return deepcopy(self)
	
	def __deepcopy__(self, memo):
		copyList: list[Vote[VoteType]] = list[Vote[VoteType]]()
		vote: Vote
		for vote in self.votes.values():
			copyList.append(deepcopy(vote))
		ret = RunningVote(copyList, self.dealerItemVotes.copy())
		memo[id(self)] = ret
		return ret

	def __iter__(self):
		if not self.sorted:
			self.sort()
		return iter(self.votes)
	
	def __len__(self):
		return len(self.votes)
	
	def items(self):
		return self.votes.items()

	def sort(self) -> None:
		if self.sorted:
			return
		voteCountSet: set[int] = set()
		vote: Vote
		for vote in self.votes.values():
			voteCountSet.add(vote.getNumVotes())
		voteCountList: list[int] = list(voteCountSet)
		voteCountList.sort(reverse = True)
		
		beforeSort: OrderedDict[str, Vote] = self.votes.copy()

		voteVal: str
		for nextVoteCount in iter(voteCountList):
			for voteVal, vote in beforeSort.items():
				if vote.getNumVotes() == nextVoteCount:
					self.votes.move_to_end(voteVal)
		self.sorted = True

	def addAVote(self, vote: VoteType | Vote[VoteType]) -> None:
		self.totalVotes += 1
		voteStr: str = str(vote)
		
		dealerVoteIndex: int = self.extractDealerVoteIndex(voteStr) #0 indexed
		isAdrenaline: bool = dealerVoteIndex >= 0
		logger.debug(f"Latest vote \"{voteStr}\" has a dealer vote of \"{dealerVoteIndex}\"")
		if isAdrenaline:
			self.dealerItemVotes[dealerVoteIndex] += 1 #0 indexed
			logger.debug(f"Dealer Item Votes after the latest dealer vote: {self.dealerItemVotes}")
		
		voteStr = " ".join(voteStr.split(" ")[0: 2]) #Remove dealer vote to combine votes for the same item with different dealer votes into one.

		if voteStr in self.votes:
			self.votes[voteStr].addAVote()
		else:
			if type(vote) is str:
				logger.debug(f"Adding new vote. Constructing from string \"{vote}\"")
				self.votes[voteStr] = Vote[VoteType](vote, 1, isAdrenaline)
			elif type(vote) is Vote[VoteType]:
				logger.debug(f"Adding new vote. Constructing from Vote. Type: {type(vote)}. Vote val: {vote}")
				vote.numVotes = 1
				self.votes[voteStr] = vote
			elif issubclass(type(vote), VoteType.__constraints__):
				logger.debug(f"Adding new vote. Constructing from VoteType subtype. Type: {type(vote)}. Vote val: {vote}")
				newVote: Vote[VoteType] = Vote[VoteType](vote, 1, isAdrenaline) # type: ignore   At this point I know it's a VoteType but python doesn't realize it, and doesn't allow me to cast to tell it it's fine
				self.votes[voteStr] = newVote
		self.sorted = False
	
	def extractDealerVoteIndex(self, voteStr: str) -> int:
		voteSplit: list[str] = voteStr.split(" ")
		if len(voteSplit) <= 2: #More than 2 entries means dealer vote
			return -1
		dealerVote: str = voteSplit[2]
		if len(dealerVote) != 1:
			logger.warn(f"Expected dealer vote \"{dealerVote}\" from vote \"{voteStr}\" to be a single character. Was {len(dealerVote)}")
			return -1
		if not dealerVote.isdigit():
			logger.warn(f"Expected dealer vote \"{dealerVote}\" from vote \"{voteStr}\" to only contain a digit. Was not a digit.")
			return -1
		return int(dealerVote) - 1 #Turn into zero index. Votes are given 1 indexed.

	def removeAVote(self, vote: VoteType | Vote[VoteType]) -> None:
		self.totalVotes -= 1
		voteStr: str = str(vote)
		if voteStr in self.votes:
			newCount: int = self.votes[voteStr].removeAVote()
			#Don't leave old votes with no one voting for them around to clog things up
			if newCount < 1:
				self.removeVote(voteStr)
		self.sorted = False
	
	#To be used if vote is invalid
	def removeVote(self, vote: str | VoteType | Vote[VoteType]) -> None:
		voteStr: str = str(vote)
		if voteStr in self.votes:
			voteFound: Vote = self.votes.pop(voteStr)
			self.totalVotes -= voteFound.getNumVotes()
			#NOT setting sorted flag to false. Since this is just removing something from the list, an already sorted one should stay sorted
	
	def getTotalVotes(self) -> int:
		return self.totalVotes

	def clear(self) -> None:
		self.totalVotes = 0
		self.votes.clear()
		self.sorted = True
	
	def hasVotes(self) -> bool:
		return self.totalVotes > 0
	
	def getAdrenalineItemVotes(self) -> list[int]:
		return self.dealerItemVotes

class VotingTallyEntry(Generic[VoteType]):
	def __init__(self, vote: Vote[VoteType], totalVotes: int, adrenalineItemVote: int = -1):
		self.vote = vote
		self.totalVotes: int = totalVotes #Used only for copy
		self.percentageRaw: float = 0
		if vote.getNumVotes() > 0 and totalVotes > 0:
			self.percentageRaw = float(vote.getNumVotes())*100/totalVotes
		self.percentageRound: float = round(self.percentageRaw)
		self.adrenalineItemVote = adrenalineItemVote
		
	def __copy__(self):
		return deepcopy(self)
	
	def __deepcopy__(self, memo):
		ret = VotingTallyEntry(deepcopy(self.vote), self.totalVotes, self.adrenalineItemVote)
		memo[id(self)] = ret
		return ret

	def changeTotalVotes(self, newTotalVote: int) -> None:
		self.totalVotes = newTotalVote
		self.recalculate()
		
	def recalculate(self):
		self.percentageRaw = float(self.vote.getNumVotes())*100/self.totalVotes
		self.percentageRound = round(self.percentageRaw)

	def getVoteObj(self) -> Vote[VoteType]:
		return self.vote

	def getBaseVoteStr(self) -> str:
		voteStr: str = str(self.vote.getVote()).upper()
		voteStrSplit: list[str] = voteStr.split(" ")
		return f"{voteStrSplit[0]} {voteStrSplit[1]}"

	def getVoteStr(self) -> str:
		adrenalineAddition: str = ""
		if self.getVoteObj().isAdrenalineItem():
			adrenalineAddition = f" {self.adrenalineItemVote}"
		logger.debug(f"Base vote: [{self.vote.getVote()}]. Addition: [{adrenalineAddition}]")
		return f"{self.vote.getVote()}{adrenalineAddition}"
	
	def getNumVotes(self) -> int:
		return self.vote.getNumVotes()
	
	def getPercentageRaw(self) -> float:
		return self.percentageRaw
	
	def getPercentageRound(self) -> float:
		return self.percentageRound
	
	def getPercentageStr(self) -> str:
		return f"{self.percentageRound}%"

class VotingTallyEntryList(Generic[VoteType]):
	def __init__(self, tallyVoteCountToContain: int, tallies: list[VotingTallyEntry[VoteType]] | None = None):
		self.tallyVoteCountToContain = tallyVoteCountToContain
		if tallies is None:
			tallies = list[VotingTallyEntry[VoteType]]()
		self.tallies: list[VotingTallyEntry[VoteType]] = tallies
		self.chosenRandomly: bool = False
		random.shuffle(self.tallies)
		self.winnerIter = iter(self.tallies)
		
	def __lt__(self, other):
		return self.getTallyVoteCountToContain() < other.getTallyVoteCountToContain()
	
	def __copy__(self):
		return deepcopy(self)

	def __deepcopy__(self, memo):
		copiedList: list[VotingTallyEntry] = list[VotingTallyEntry]()
		entry: VotingTallyEntry
		for entry in self.tallies:
			copiedList.append(deepcopy(entry))
		ret = VotingTallyEntryList(self.tallyVoteCountToContain, copiedList)
		memo[id(self)] = ret
		return ret
	
	#TODO: There should probably be two kinds of EntryList. Those that can choose randomly and those that can't
	def getWinner(self) -> VotingTallyEntry[VoteType] | None:
		if not self.hasSingleWinner(): #Not allowed to break ties for this method, and obviously no winner if no tallies
			return None
		return self.tallies[0]

	def getRandomWinner(self) -> VotingTallyEntry[VoteType] | None:
		if len(self.tallies) < 1:
			return None
		if len(self.tallies) > 1:
			self.chosenRandomly = True
		return next(self.winnerIter, None)

	def getTallyVoteCountToContain(self) -> int:
		return self.tallyVoteCountToContain

	def add(self, tallyEntry: VotingTallyEntry[VoteType]) -> bool:
		if tallyEntry.getNumVotes() != self.tallyVoteCountToContain:
			return False
		self.tallies.append(tallyEntry)
		return True
	
	def count(self) -> int:
		return len(self.tallies)

	def hasSingleWinner(self) -> bool:
		return len(self.tallies) == 1

	def tie(self) -> bool:
		return len(self.tallies) > 1
	
	def removeVote(self, voteToRemove: str | VoteType) -> int:
		voteToRemoveStr: str = ""
		if type(voteToRemove) is str:
			voteToRemoveStr = voteToRemove
		else:
			voteToRemoveStr = str(voteToRemove)
		i: int = 0
		tallyEntry: VotingTallyEntry
		found: bool = False
		for i, tallyEntry in enumerate(self.tallies):
			if tallyEntry.getVoteStr == voteToRemoveStr:
				found = True
				break
		if found:
			return self.tallies.pop(i).getNumVotes()
		return 0
	
	def recalculate(self, newTotalVotes: int):
		for tallyEntry in self.tallies:
			tallyEntry.changeTotalVotes(newTotalVotes)
			
	def chosenRanomly(self) -> bool:
		return self.chosenRandomly

class VotingTally(Generic[VoteType]):
	def __init__(self, runningVote: RunningVote[VoteType]):
		runningVote.sort()
		self.totalVotes = runningVote.getTotalVotes()
		logger.debug(f"VotingTally.__init__, provided runningVote had {self.totalVotes} total votes")
		self.adrenalineItemVotes: list[int] = runningVote.getAdrenalineItemVotes()
		self.winningAdrenalineItemVote = self.getWinningAdrenalineItemVote()
		self.tallies: list[VotingTallyEntryList] = list[VotingTallyEntryList]()
		voteVal: str
		voteObj: Vote
		for voteVal, voteObj in runningVote.items():
			tallyEntry: VotingTallyEntry[VoteType] = VotingTallyEntry[VoteType](voteObj, self.totalVotes, self.winningAdrenalineItemVote)
			entryList: VotingTallyEntryList[VoteType] = self.getTalleyListForVoteCount(voteObj.getNumVotes())
			entryList.add(tallyEntry)
			logger.debug(f"Created vote talley entry: {tallyEntry}")
		self.tallies.sort(reverse = True)
		
		self.talliesIter : Iterator[VotingTallyEntryList[VoteType]] | None = None
		self.currentTallyList: VotingTallyEntryList[VoteType] | None
		if len(self.tallies) > 0:
			logger.debug("Found tallies in VotingTally, creating iterators")
			self.talliesIter = iter(self.tallies)
			self.currentTallyList = next(self.talliesIter, None)
		else: 
			logger.debug("No tallies in VotingTally, so no iterators")
	
	def getAdrenalineItemVotes(self) -> list[VotingTallyEntry[int]]:
		total: int = sum(self.adrenalineItemVotes)
		ret: list[VotingTallyEntry[int]] = list[VotingTallyEntry[int]]()
		for i, adrenalineItemVoteCount in enumerate(self.adrenalineItemVotes):
			vote: Vote = Vote[int](i + 1, adrenalineItemVoteCount, True)
			entry: VotingTallyEntry = VotingTallyEntry(vote, total, 0)
			ret.append(entry)
		return ret

	def getWinningAdrenalineItemVote(self) -> int:
		topVoteVoteCount: int = max(self.adrenalineItemVotes)
		ties: list[int] = list[int]()
		for vote in self.adrenalineItemVotes:
			if vote == topVoteVoteCount:
				ties.append(vote)
		if len(ties) > 1:
			logger.debug(f"There was a {len(ties)}-way tie for adrenaline vote.")
		return random.choice(ties)

	def getWinner(self) -> VotingTallyEntry[VoteType] | None:
		if not self.hasTallies():
			return None
		first: VotingTallyEntryList = self.tallies[0]
		if first.hasSingleWinner():
			return first.getWinner()
		return None
		
	def getNextWinner(self) -> VotingTallyEntry[VoteType] | None:
		if not self.hasTallies():
			return None
		return self.iterateWinner()

	def hasTallies(self) -> bool:
		return len(self.tallies) > 0

	def allVotes(self) -> list[VotingTallyEntry[VoteType]]:
		logger.info(f"allVotes start")
		allVotes: list[VotingTallyEntry] = list[VotingTallyEntry]()
		nextVote: VotingTallyEntry | None = self.iterateWinner()
		while nextVote is not None:
			logger.info(f"allVotes Added vote")
			allVotes.append(nextVote)
			nextVote = self.iterateWinner()
		return allVotes

	def topNVotes(self, n: int) -> list[VotingTallyEntry[VoteType]]:
		logger.info("Getting top votes")
		vals: list[VotingTallyEntry] = list[VotingTallyEntry]()
		for i in range(n):
			nextWinner: VotingTallyEntry | None = self.iterateWinner()
			if nextWinner is None:
				return vals
			vals.append(nextWinner)
		return vals

	def iterateWinner(self) -> VotingTallyEntry[VoteType] | None:
		#Check if anything to iterate through
		if self.talliesIter is None:
			logger.info("Cannot iterate winner. talliesIter is None")
			return None
		nextWinner: VotingTallyEntry[VoteType] | None = None 
		#Check if current entryList empty
		if self.currentTallyList is not None:
			nextWinner = self.currentTallyList.getRandomWinner() #Random winner iterates
		logger.debug(f"iterateWinner nextWinner at first check is {nextWinner}")
		if nextWinner is None:
			#If it returned None then it's empty, move to the next entry list
			self.currentTallyList = next(self.talliesIter, None)
			logger.debug(f"iterateWinner because nextWinner was None at first check, go to next tally entry list, which was {self.currentTallyList}")
			if self.currentTallyList is None:
				#Out of winners, set iter to None as an easy marker for next time
				self.talliesIter = None
				logger.debug("No next tally list, thus no more winners. Returning None.")
				return None
			#Call recursively to check for a winner in this list
			logger.debug("Found new tally entry list. Recursing to iterateWinner.")
			return self.iterateWinner()
		#If it did find a winner in this list, return them
		logger.debug(f"Found a winner. nextWinner: {nextWinner}")
		return nextWinner

	def getTalleyListForVoteCount(self, voteCount: int) -> VotingTallyEntryList:
		entryList: VotingTallyEntryList
		for entryList in self.tallies:
			if entryList.getTallyVoteCountToContain() == voteCount:
				return entryList
		entryList = VotingTallyEntryList(voteCount, list[VotingTallyEntry]())
		self.tallies.append(entryList)
		return entryList
	
	def removeVote(self, voteToRemove: str | VoteType) -> None:
		entryList: VotingTallyEntryList[VoteType]
		removedCount: int = 0
		for entryList in self.tallies:
			removedCount = entryList.removeVote(voteToRemove)
			if removedCount > 0:
				break
		#Found deleted entries, recalculate
		if removedCount > 0:
			self.totalVotes -= removedCount
			for entryList in self.tallies:
				entryList.recalculate(self.totalVotes)
			
	def numNamesTied(self) -> int:
		if self.currentTallyList is None:
			return 0
		return self.currentTallyList.count()

	def chosenRandomly(self) -> bool:
		if self.currentTallyList is None:
			return False
		return self.currentTallyList.chosenRanomly()
				

#Can't be a method of RunningVote (which would be preferable) because VotingTally isn't defined yet
#   And can't move the order because VotingTally depends on the definition of RunningVote	
def tallyVotes(runningVote: RunningVote) -> VotingTally:
	return VotingTally(runningVote)