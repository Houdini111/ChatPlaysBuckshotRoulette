from abc import abstractmethod, ABC
import tkinter as tk
import logging

from shared.util import resizeXFrom1440p, resizePointFrom1440p, Point
from shared.actions import Action, ShootAction, UseItemAction
from shared.consts import Target
from bot.vote import VotingTallyEntry, Vote

logger = logging.getLogger(__name__)

class Circle:
	def __init__(self, canvas: tk.Canvas, position: Point = Point(0, 0), tags: list[str] = list[str]()):
		self.canvas = canvas
		width1440 = 10
		self.r = 50
		self.scaledWidth = resizeXFrom1440p(width1440)
		self.circle = None
		self.lastX = position.x
		self.lastY = position.y
		self.init_circle(position, self.r, tags= tags)

	def show(self) -> None:
		logger.debug(f"Circle ID: {self.circle} being shown")
		self.canvas.itemconfigure(self.circle, state="normal")

	def hide(self) -> None:
		logger.debug(f"Circle ID: {self.circle} being hidden")
		self.canvas.itemconfigure(self.circle, state="hidden")

	def solid(self) -> None:
		pass #TODO: Show solid, hide dotted
	
	def dotted(self) -> None:
		pass #TODO: Show dotted, hide solid
	
	def init_circle(self, p1440: Point, r, tags: list[str] = list[str]()) -> int: #center coordinates, radius
		logging.debug(f"Circle ID: {self.circle} creating reticle at 1440p cooridinates of {p1440}. Previous position: ({self.lastX}, {self.lastY}).")
		self.lastX = p1440.x
		self.lastY = p1440.y
		pScaled: Point = resizePointFrom1440p(p1440)
		x0 = pScaled.x - r
		y0 = pScaled.y - r
		x1 = pScaled.x + r
		y1 = pScaled.y + r
		self.circle = self.canvas.create_oval(x0, y0, x1, y1, outline = "red", width = self.scaledWidth, tags= tags)
		self.hide()

	def move(self, p1440: Point) -> int:
		if self.lastX == p1440.x and self.lastY == p1440.y:
			return #Same. Don't bother moving
		self.lastX = p1440.x
		self.lastY = p1440.y
		
		#recenteredPoint: Point = Point(p1440.x - self.r, p1440.y - self.r)
		#pScaled = resizePointFrom1440p(recenteredPoint)
		
		pScaled = resizePointFrom1440p(p1440)

		oldId: int = self.circle
		oldTags = self.canvas.gettags(oldId)
		self.init_circle(pScaled, self.r, tags= oldTags)
		self.canvas.delete(oldId)
		
	def show_at(self, p1440: Point) -> None:
		self.move(p1440)
		self.show()

class DealerActionReticle(): 
	def __init__(self, canvas: tk.Canvas):
		self.canvas = canvas
		self.dealerReticleTag = "dealerReticleTag"
		dealerReticleTagList = list[str]()
		dealerReticleTagList.append(self.dealerReticleTag)
		
		positions: list[Point] = list[Point]() #Zero indexed
		positions.append(Point(892, 190))  #1
		positions.append(Point(1043, 190)) #2
		positions.append(Point(1507, 190)) #3
		positions.append(Point(1663, 190)) #4
		positions.append(Point(839, 310))  #5
		positions.append(Point(1011, 310)) #6
		positions.append(Point(1552, 310)) #7
		positions.append(Point(1717, 310)) #8
		
		self.reticles: list[Circle] = list[Circle]()
		for pos in positions:
			circle: Circle = Circle(self.canvas, position= pos, tags= dealerReticleTagList)
			circle.hide()
			self.reticles.append(circle)
		self.reticleState: dict[int, bool] = dict[int, bool]()
		for i in range(1, 9): #[1: 9)
			self.reticleState[i] = False

	def showFor(self, winnerList: list[VotingTallyEntry] | None) -> None:
		if winnerList is None or len(winnerList) < 1:
			logging.debug("DealerActionReticle given no winners. Hiding.")
			return
		self.show()

		votedNumbers: list[int] = list[int]()
		for winner in winnerList:
			voteObj: Vote = winner.getVoteObj()
			adrenalineItem: int = voteObj.getVote()
			
			#1 indexed?
			if adrenalineItem < 1 or adrenalineItem > 8:
				logging.debug(f"DealerActionReticle given bad value. Ignoring. Value: {adrenalineItem}")
				continue
			votedNumbers.append(adrenalineItem)

		logger.debug(f"DealerActionReticle voted numbers: {votedNumbers}")
		for number in range(1, 9): #[1: 9)
			if number in votedNumbers:
				self.reticles[number - 1].show()
			else:
				self.reticles[number - 1].hide()

		
	def show(self) -> None:
		logging.debug("DealerActionReticle told to show.")
		self.canvas.itemconfigure(self.dealerReticleTag, state="normal")
		
	def hide(self) -> None:
		logging.debug("DealerActionReticle told to hide.")
		self.canvas.itemconfigure(self.dealerReticleTag, state="hidden")

class PlayerActionReticle(): 
	def __init__(self, canvas: tk.Canvas):
		self.canvas = canvas
		self.circle: Circle = Circle(canvas)
		
		self.shootDealerPosition = Point(1275, 325)
		self.shootSelfPosition = Point(1275, 780)

		self.itemPositions: list[Point] = list[Point]() #Zero indexed
		self.itemPositions.append(Point(690, 600))  #1
		self.itemPositions.append(Point(915, 600)) #2
		self.itemPositions.append(Point(1650, 600)) #3
		self.itemPositions.append(Point(1860, 600)) #4
		self.itemPositions.append(Point(525, 915))  #5
		self.itemPositions.append(Point(815, 915)) #6
		self.itemPositions.append(Point(1725, 915)) #7
		self.itemPositions.append(Point(2025, 915)) #8

	def showFor(self, tallyEntry: VotingTallyEntry | None) -> None:
		if tallyEntry is None:
			self.circle.hide()
			logging.debug("PlayerActionReticle given bad value. Hiding.")
			return

		voteObj: Vote = tallyEntry.getVoteObj()
		vote: Action = voteObj.getVote()

		oldId: int = self.circle.circle
		if type(vote) == UseItemAction:
			#1 indexed?
			itemNum: int = vote.getItemNum()
			logging.debug(f"PlayerActionReticle given item vote: {itemNum}")
			self.circle.show_at(self.itemPositions[itemNum - 1])
		elif type(vote) == ShootAction:
			target: Target = vote.getTarget()
			logging.debug(f"PlayerActionReticle given shoot vote: {target}")
			if target == Target.DEALER:
				self.circle.show_at(self.shootDealerPosition)
			elif target == Target.SELF:
				self.circle.show_at(self.shootSelfPosition)
		logger.debug(f"PlayerActionReticle old ID {oldId} replaced with new ID {self.circle.circle}")
		
	def hide(self) -> None:
		logging.debug("PlayerActionReticle told to hide.")
		self.circle.hide()
		
class WinningActionReticle(ABC): 
	def __init__(self, canvas: tk.Canvas):
		self.canvas = canvas
		
		self.playerReticle: PlayerActionReticle = PlayerActionReticle(canvas)
		self.dealerReticle: DealerActionReticle = DealerActionReticle(canvas)
		
	def getWinningVoteActionToShow(self, votes: list[VotingTallyEntry], allowTie: bool = False) -> VotingTallyEntry | None:
		if len(votes) < 1:
			if allowTie:
				return list[VotingTallyEntry]()
			else:
				return None

		logger.debug(f"Dealer reticle votes to show: {votes}. Count: {len(votes)}")
		vote: VotingTallyEntry
		winners: list[VotingTallyEntry] = list[VotingTallyEntry]()
		maxVoteNum: int = 0
		for vote in votes:
			thisVoteNum: int = vote.getNumVotes()
			if thisVoteNum < 1:
				continue
			
			if thisVoteNum > maxVoteNum:
				maxVoteNum = thisVoteNum
				winners.clear()
				winners.append(vote)
			elif thisVoteNum == maxVoteNum:
				winners.append(vote)
			
		if allowTie:
			return winners
		
		#Ties not allowed, return the winner if there is only one
		if len(winners) == 1:
			return winners[0]
		#Otherwise there is no winner
		return None
		
	def showForList(self, actionVotes: list[VotingTallyEntry], adrenalineItemVotes: list[VotingTallyEntry]) -> None:
		winningActionVote = None
		if actionVotes is not None:
			winningActionVote = self.getWinningVoteActionToShow(actionVotes)
		
		winningDealerItemVotes: list[VotingTallyEntry] = list[VotingTallyEntry]()
		if adrenalineItemVotes is not None:
			actualVotesForAdrenalineItems: list[VotingTallyEntry] = list[VotingTallyEntry]()
			for voteEntry in adrenalineItemVotes:
				if voteEntry.getNumVotes() > 0:
					actualVotesForAdrenalineItems.append(voteEntry)
			winningDealerItemVotes = self.getWinningVoteActionToShow(actualVotesForAdrenalineItems, allowTie=True)
			logger.debug(f"Winning dealer reticle votes: {winningDealerItemVotes}. Count: {len(winningDealerItemVotes)}")

		#logger.debug(f"Reticles to show for types: {type(winningActionVote)} and {type(winningDealerItemVote)}")
		self.showFor(winningActionVote, winningDealerItemVotes)

	def showFor(self, playerVoteTallyEntry: VotingTallyEntry, dealerVoteTallyEntry: list[VotingTallyEntry]) -> None:
		self.playerReticle.showFor(playerVoteTallyEntry)
		self.dealerReticle.showFor(dealerVoteTallyEntry)
		
	def hide(self) -> None:
		logging.debug("WinningActionReticle told to hide.")
		self.playerReticle.hide()
		self.dealerReticle.hide()