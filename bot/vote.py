from collections import defaultdict
from os import remove
import random
from typing import OrderedDict
from copy import copy, deepcopy


class Vote():
	def __init__(self, vote: str, numVotes: int):
		self.vote = vote
		self.numVotes = numVotes
	
	def __lt__(self, other):
		return self.numVotes < other.numVotes
	
	def __copy__(self):
		return self.__deepcopy__()
	
	def __deepcopy__(self):
		return Vote(self.vote, self.numVotes)
	
	def getVote(self) -> str:
		return self.vote
	
	def getNumVotes(self) -> int:
		return self.numVotes
	
	def addAVote(self) -> int:
		self.numVotes += 1
		return self.numVotes
	
	def removeAVote(self) -> int:
		self.numVotes -= 1
		return self.numVotes

class RunningVote():
	def __init__(self, votes: list[Vote] | None = None):
		self.votes: OrderedDict[str, Vote] = OrderedDict()
		self.totalVotes = 0
		self.sorted = True

		if votes is not None:
			self.sorted = False
			for vote in votes:
				self.totalVotes += vote.getNumVotes()
			for vote in votes:
				self.votes[vote.getVote()] = vote
		self.sort()	
		
	def __copy__(self):
		return self.__deepcopy__()
	
	def __deepcopy__(self):
		copyList: list[Vote] = []
		vote: Vote
		for vote in self.votes.values():
			copyList.append(copy(vote))
		return RunningVote(copyList)

	def __iter__(self):
		if not self.sorted:
			self.sort()
		return iter(self.votes)
	
	def items(self):
		return self.votes.items()

	def sort(self) -> None:
		if self.sorted:
			return
		voteCountList: list[int] = []
		vote: Vote
		for vote in self.votes.values():
			voteCountList.append(vote.getNumVotes())
		voteCountList.sort()
		voteCountSet: set[int] = set(voteCountList)
		
		oldDict: OrderedDict[str, Vote] = self.votes.copy()

		voteVal: str
		for nextVoteCount in iter(voteCountSet):
			for voteVal, vote in oldDict.items():
				if vote.getNumVotes() == nextVoteCount:
					self.votes.move_to_end(voteVal)
		self.sorted = True

	def addAVote(self, vote: str | Vote) -> None:
		self.totalVotes += 1
		voteVal: str = self.getVoteVal(vote)
		if voteVal in self.votes:
			self.votes[voteVal].addAVote()
		self.sorted = False
	
	def removeAVote(self, vote: str | Vote) -> None:
		self.totalVotes -= 1
		voteVal: str = self.getVoteVal(vote)
		if voteVal in self.votes:
			self.votes[voteVal].removeAVote()
		self.sorted = False
	
	#To be used if vote is invalid
	def removeVote(self, vote: str | Vote) -> None:
		voteVal: str = self.getVoteVal(vote)
		if voteVal in self.votes:
			voteFound: Vote = self.votes.pop(voteVal)
			self.totalVotes -= voteFound.getNumVotes()
			#NOT setting sorted flag to false. Since this is just removing something from the list, an already sorted one should stay sorted
	
	def getVoteVal(self, vote: str | Vote) -> str:
		if type(vote) is str:
			return vote
		elif type(vote) is Vote:
			return vote.getVote()
		return ""
	
	def getTotalVotes(self) -> int:
		return self.totalVotes

	def clear(self) -> None:
		self.totalVotes = 0
		self.votes.clear()
		self.sorted = True
	
	def hasVotes(self) -> bool:
		return self.totalVotes > 0

class VotingTallyEntry():
	def __init__(self, vote: Vote, totalVotes: int):
		self.vote = vote
		self.totalVotes: int = totalVotes #Used only for copy
		self.percentageRaw: float = float(vote.getNumVotes())*100/totalVotes
		self.percentageRound: float = round(self.percentageRaw)
		
	def __copy__(self):
		return self.__deepcopy__()
	
	def __deepcopy__(self):
		return VotingTallyEntry(copy(self.vote), self.totalVotes)

	def changeTotalVotes(self, newTotalVote: int) -> None:
		self.totalVotes = newTotalVote
		self.recalculate()
		
	def recalculate(self):
		self.percentageRaw = float(self.vote.getNumVotes())*100/self.totalVotes
		self.percentageRound = round(self.percentageRaw)

	def getVoteObj(self) -> Vote:
		return self.vote
	
	def getVote(self) -> str:
		return self.vote.getVote()
	
	def getNumVotes(self) -> int:
		return self.vote.getNumVotes()
	
	def getPercentageRaw(self) -> float:
		return self.percentageRaw
	
	def getPercentageRound(self) -> float:
		return self.percentageRound
	
	def getPercentageStr(self) -> str:
		return f"{self.percentageRound}%"

class VotingTallyEntryList():
	def __init__(self, tallyVoteCountToContain: int, tallies: list[VotingTallyEntry] | None = None):
		self.tallyVoteCountToContain = tallyVoteCountToContain
		if tallies is None:
			tallies = []
		self.tallies = tallies
		self.chosenRandomly: bool = False
		random.shuffle(self.tallies)
		self.winnerIter = iter(self.tallies)
		
	def __lt__(self, other):
		return self.getTallyVoteCountToContain < other.getTallyVoteCountToContain()
	
	def __copy__(self):
		return self.__deepcopy__()
	
	def __deepcopy__(self):
		copiedList: list[VotingTallyEntry] = []
		entry: VotingTallyEntry
		for entry in self.tallies:
			copiedList.append(copy(entry))
		return VotingTallyEntryList(self.tallyVoteCountToContain, copiedList)
	
	#TODO: There should probably be two kinds of EntryList. Those that can choose randomly and those that can't
	def getWinner(self) -> VotingTallyEntry | None:
		if not self.hasSingleWinner(): #Not allowed to break ties for this method, and obviously no winner if no tallies
			return None
		return self.tallies[0]

	def getRandomWinner(self) -> VotingTallyEntry | None:
		if len(self.tallies) < 1:
			return None
		if len(self.tallies) > 0:
			self.chosenRandomly = True
		return next(self.winnerIter, None)

	def getTallyVoteCountToContain(self) -> int:
		return self.tallyVoteCountToContain

	def add(self, tallyEntry: VotingTallyEntry) -> bool:
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
	
	def removeVote(self, voteToRemove: str) -> int:
		i: int = 0
		tallyEntry: VotingTallyEntry
		found: bool = False
		for i, tallyEntry in enumerate(self.tallies):
			if tallyEntry.getVote == voteToRemove:
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

class VotingTally():
	def __init__(self, runningVote: RunningVote):
		runningVote.sort()
		self.totalVotes = runningVote.getTotalVotes()
		self.tallies: list[VotingTallyEntryList] = []
		voteVal: str
		voteObj: Vote
		for voteVal, voteObj in runningVote.items():
			tallyEntry: VotingTallyEntry = VotingTallyEntry(voteObj, self.totalVotes)
			entryList: VotingTallyEntryList = self.getTalleyListForVoteCount(voteObj.getNumVotes())
			entryList.add(tallyEntry)
		self.tallies.sort()
		
		self.talliesIter = None
		self.currentTallyList: VotingTallyEntryList
		if len(self.tallies) > 0:
			self.talliesIter = iter(self.tallies)
			self.currentTallyList = next(self.talliesIter)
	
	def getWinner(self) -> VotingTallyEntry | None:
		if not self.hasTallies():
			return None
		first: VotingTallyEntryList = self.tallies[0]
		if first.hasSingleWinner():
			return first.getWinner()
		return None
		
	def getNextWinner(self) -> VotingTallyEntry | None:
		if not self.hasTallies():
			return None
		return self.iterateWinner()

	def hasTallies(self) -> bool:
		return len(self.tallies) > 0

	def iterateWinner(self) -> VotingTallyEntry | None:
		#Check if anything to iterate through
		if self.talliesIter is None:
			return None
		#Check if current entryList empty
		nextWinner: VotingTallyEntry | None = self.currentTallyList.getRandomWinner()
		if nextWinner is None:
			#If it returned None then it's empty, move to the next entry list
			nextTallyList: VotingTallyEntryList | None = next(self.talliesIter, None)
			if nextTallyList is None:
				#Out of winners, set iter to None as an easy marker for next time
				self.talliesIter = None
				return None
			#Otherwise, if it found a new list, use that for the next attempt
			self.currentTallyList = nextTallyList
			#Call recursively to check for a winner in this list
			return self.iterateWinner()
		#If it did find a winner in this list, return them
		return nextWinner

	def getTalleyListForVoteCount(self, voteCount: int) -> VotingTallyEntryList:
		entryList: VotingTallyEntryList
		for entryList in self.tallies:
			if entryList.getTallyVoteCountToContain() == voteCount:
				return entryList
		entryList = VotingTallyEntryList(voteCount)
		self.tallies.append(entryList)
		return entryList
	
	def removeVote(self, voteToRemove: str) -> None:
		entryList: VotingTallyEntryList
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