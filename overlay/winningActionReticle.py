from abc import abstractmethod, ABC
import tkinter as tk
import logging

from shared.util import resizeXFrom1440p, resizePointFrom1440p, Point
from shared.actions import Action, ShootAction, UseItemAction
from shared.consts import Target
from bot.vote import VotingTallyEntry, Vote

logger = logging.getLogger(__name__)

class Circle:
	def __init__(self, canvas: tk.Canvas):
		self.canvas = canvas
		width1440 = 10
		self.r = 50
		self.scaledWidth = resizeXFrom1440p(width1440)
		self.init_circle(Point(0, 0), self.r)

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
	
	def init_circle(self, p1440: Point, r) -> int: #center coordinates, radius
		self.lastX = p1440.x
		self.lastY = p1440.y
		pScaled: Point = resizePointFrom1440p(p1440)
		x0 = pScaled.x - r
		y0 = pScaled.y - r
		x1 = pScaled.x + r
		y1 = pScaled.y + r
		self.circle = self.canvas.create_oval(x0, y0, x1, y1, outline = "red", width = self.scaledWidth)
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
		self.init_circle(pScaled, self.r)
		self.canvas.delete(oldId)
		
	def show_at(self, p1440: Point) -> None:
		self.move(p1440)
		self.show()

class DealerActionReticle(): 
	def __init__(self, canvas: tk.Canvas):
		self.canvas = canvas
		self.circle: Circle = Circle(canvas)
		
		self.positions: list[Point] = list[Point]() #Zero indexed
		self.positions.append(Point(892, 190))  #1
		self.positions.append(Point(1043, 190)) #2
		self.positions.append(Point(1507, 190)) #3
		self.positions.append(Point(1663, 190)) #4
		self.positions.append(Point(839, 310))  #5
		self.positions.append(Point(1011, 310)) #6
		self.positions.append(Point(1552, 310)) #7
		self.positions.append(Point(1717, 310)) #8

	def showFor(self, tallyEntry: VotingTallyEntry | None) -> None:
		if tallyEntry is None:
			self.circle.hide()
			logging.debug("DealerActionReticle given NONE value. Hiding.")
			return

		voteObj: Vote = tallyEntry.getVoteObj()
		adrenalineItem: int = voteObj.getVote()

		#1 indexed?
		if adrenalineItem < 1 or adrenalineItem > 8:
			self.circle.hide()
			logging.debug(f"DealerActionReticle given bad value. Hiding. Value: {adrenalineItem}")
			return
		logging.debug(f"DealerActionReticle given dealer vote: {adrenalineItem}")
		circlePos: Point = self.positions[adrenalineItem - 1]
		self.circle.show_at(circlePos)
		
	def hide(self) -> None:
		logging.debug("DealerActionReticle told to hide.")
		self.circle.hide()

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
		
	def hide(self) -> None:
		logging.debug("PlayerActionReticle told to hide.")
		self.circle.hide()
		
class WinningActionReticle(ABC): 
	def __init__(self, canvas: tk.Canvas):
		self.canvas = canvas
		
		self.playerReticle: PlayerActionReticle = PlayerActionReticle(canvas)
		self.dealerReticle: DealerActionReticle = DealerActionReticle(canvas)
		
	def getWinningVoteActionToShow(self, votes: list[VotingTallyEntry]) -> VotingTallyEntry | None:
		sortedVotes: list[VotingTallyEntry] = sorted(votes, key = lambda vote: (vote.getNumVotes(), vote.getBaseVoteStr()))		
		winningVote = None
		if len(sortedVotes) > 0:
			winningVote = sortedVotes[0]
			if len(sortedVotes) > 1:
				other = sortedVotes[1]
				if winningVote.getNumVotes() == other.getNumVotes():
					winningVote = None
		return winningVote
		
	def showForList(self, actionVotes: list[VotingTallyEntry], adrenalineItemVotes: list[VotingTallyEntry]) -> None:
		winningActionVote = None
		if actionVotes is not None:
			winningActionVote = self.getWinningVoteActionToShow(actionVotes)
		
		winningDealerItemVote = None
		if adrenalineItemVotes is not None:
			actualVotesForAdrenalineItems: list[VotingTallyEntry] = list[VotingTallyEntry]()
			for voteEntry in adrenalineItemVotes:
				if voteEntry.getNumVotes() > 0:
					actualVotesForAdrenalineItems.append(voteEntry)
			winningDealerItemVote = self.getWinningVoteActionToShow(actualVotesForAdrenalineItems)					

		logger.debug(f"Reticles to show for types: {type(winningActionVote)} and {type(winningDealerItemVote)}")
		self.showFor(winningActionVote, winningDealerItemVote)

	def showFor(self, playerVoteTallyEntry: VotingTallyEntry, dealerVoteTallyEntry: VotingTallyEntry) -> None:
		self.playerReticle.showFor(playerVoteTallyEntry)
		self.dealerReticle.showFor(dealerVoteTallyEntry)
		
	def hide(self) -> None:
		logging.debug("WinningActionReticle told to hide.")
		self.playerReticle.hide()
		self.dealerReticle.hide()