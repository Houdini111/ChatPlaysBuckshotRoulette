from typing import Callable, Generic, TypeVar
import logging
import tkinter as tk

from shared.consts import Target
from shared.actions import Action, ShootAction, UseItemAction
from bot.vote import Vote, VotingTally, VotingTallyEntry
from .consts import Tags

logger = logging.getLogger(__name__)

ActionVoteType = TypeVar("ActionVoteType", int, Target)

class ActionVoteDisplay(Generic[ActionVoteType]):
	def __init__(self, actionGuide: ActionVoteType, x1440: int, y1440: int, fontSize: int, draw_text_1440: Callable, canvas: tk.Canvas):
		self.actionGuide: ActionVoteType = actionGuide
		self.x1440: int = x1440
		self.y1440: int = y1440
		self.fontSize: int = fontSize
		self.canvas: tk.Canvas = canvas
		actionGuideStr: str = str(actionGuide)
		logger.debug(f"Action Guide Str Type: {type(self)}")
		if type(self) is DealerVoteDisplay:
			actionGuideStr = ""
		self.mainTextId: int = draw_text_1440(actionGuideStr, x1440, y1440, self.fontSize, self.canvas, textTags = [Tags.ACTION_VOTE_STATIC], anchor = "center")		
		verticalOffset: int = int(fontSize * 1.1)
		horizontalOffset: int = 0 #These default values are for str actionGuides (shoot type)
		anchor: str = "center"
		if type(actionGuide) is int:
			if actionGuide % 2 == 0: #Even goes right, so anchor left
				anchor = "w"
				horizontalOffset = -60 #Also move the top numbers closer, so they're not quite so far off their root number
			else: #Odd goes left, so anchor right
				anchor = "e"
				horizontalOffset = 60 
		elif type(actionGuide) is Target:
			logger.debug("Action guide is for Targets")
			if actionGuide == Target.DEALER:
				logger.debug("Action guide is for Target DEALER")
				verticalOffset = verticalOffset * -1
		if type(self) is DealerVoteDisplay:
			if actionGuide == 2:
				verticalOffset = -17
			elif actionGuide == 3:
				verticalOffset = -70
			elif actionGuide == 6:
				verticalOffset = 27
			elif actionGuide == 7:
				verticalOffset = -27
			else:
				verticalOffset = 0
		logger.debug(f"Vertical offset for actionGuide: {actionGuide} is {verticalOffset}. Type: {type(self)}")
		self.statsTextId: int = draw_text_1440("", x1440 + horizontalOffset, y1440 - verticalOffset, int(self.fontSize * 0.5), self.canvas, textTags = [Tags.ACTION_VOTE_STATIC, Tags.ACTION_VOTE_STATS], anchor = anchor)
	
	def getActionGuide(self) -> ActionVoteType:
		return self.actionGuide

	def displayVoteGuide(self) -> None:
		logger.debug(f"Displaying vote guide for {self.actionGuide}")
		self.canvas.itemconfig(self.mainTextId, state="normal")

	def displayVote(self, voteEntry: VotingTallyEntry | None) -> None:
		logger.debug(f"{type(self)}: Displaying vote for vote guide {self.actionGuide}. Vote: {voteEntry}")
		numVotesStr: str = "0"
		percentStr: str = "0%"
		if voteEntry is not None:
			numVotesStr = str(voteEntry.getNumVotes())
			percentStr = voteEntry.getPercentageStr()
		statsText = f"{numVotesStr} ({percentStr})"
		#statsText = f"{numVotesStr} {percentStr}"
		logger.debug(f"{type(self)}: Displaying vote for vote guide {self.actionGuide}. Vote: {voteEntry}. Stats Text: \"{statsText}\"")
		self.canvas.itemconfig(self.statsTextId, text=statsText)
		self.canvas.itemconfig(self.statsTextId, state="normal")
		
	def clearVoteStats(self):
		self.canvas.itemconfigure(self.statsTextId, state="hidden")
		#self.canvas.itemconfig(self.statsTextId, text="")
		
class ItemActionVoteDisplay(ActionVoteDisplay):
	pass

class ShootActionVoteDisplay(ActionVoteDisplay):
	pass

class DealerVoteDisplay(ActionVoteDisplay):
	pass

class FullScreenVoteDisplay():
	def __init__(self, baseFontSize: int, draw_text_1440: Callable, canvas: tk.Canvas):
		self.baseFontSize = baseFontSize

		self.itemActionVoteDisplays: dict[int, ItemActionVoteDisplay] = dict[int, ItemActionVoteDisplay]()
		self.dealerItemVoteDisplays: dict[int, ItemActionVoteDisplay] = dict[int, ItemActionVoteDisplay]()
		self.lastDrawnActionNumbers: list[int] = list[int]()
		numberFontSize: int =  int(self.baseFontSize*1.2)
		voteDisplay: ActionVoteDisplay
		playerNumGridPositions = {
			1: [725, 550],	
			2: [925, 550],
			3: [1625, 550],
			4: [1850, 550],
			5: [550, 900],
			6: [850, 900],
			7: [1700, 900],
			8: [1975, 900]
		}
		for i in range(1, 9): #[1, 9)
			if i < 1 or i > 8:
				continue
			pos = playerNumGridPositions[i]
			voteDisplay = ItemActionVoteDisplay(i, pos[0], pos[1], numberFontSize, draw_text_1440, canvas)
			self.itemActionVoteDisplays[i] = voteDisplay
			#myFakeTallyEntry = VotingTallyEntry(Vote[str]("999", 999), 999)
			#voteDisplay.displayVote(myFakeTallyEntry)
		
		dealerNumGridPositions = {
			1: [790, 200],	
			2: [1121, 200],
			3: [1417, 200],
			4: [1749, 200],
			5: [700, 350],
			6: [1095, 350],
			7: [1450, 350],
			8: [1850, 350]
		}
		for i in range(1, 9): #[1, 9)
			if i < 1 or i > 8:
				continue
			pos = dealerNumGridPositions[i]
			voteDisplay = DealerVoteDisplay(i, pos[0], pos[1], int(numberFontSize *0.75), draw_text_1440, canvas)
			self.dealerItemVoteDisplays[i] = voteDisplay
			#myFakeTallyEntry = VotingTallyEntry(Vote[str]("999", 999), 999)
			#voteDisplay.displayVote(myFakeTallyEntry)
		
		self.shootActionVoteDisplays: dict[Target, ShootActionVoteDisplay] =  dict[Target, ShootActionVoteDisplay]()
		voteDisplay = ShootActionVoteDisplay(Target.DEALER, int(2560/2), self.baseFontSize, self.baseFontSize, draw_text_1440, canvas)
		#voteDisplay.displayVote(VotingTallyEntry(Vote[Target](Target.DEALER, 1), 1))
		self.shootActionVoteDisplays[Target.DEALER] = voteDisplay
		voteDisplay = ShootActionVoteDisplay(Target.SELF, int(2560/2), 1440 - self.baseFontSize, self.baseFontSize, draw_text_1440, canvas)
		self.shootActionVoteDisplays[Target.SELF] = voteDisplay
		
	#def showActionVoteStatic(self) -> None:
	#	voteDisplay: ActionVoteDisplay
	#	for voteDisplay in self.shootActionVoteDisplays.values():
	#		voteDisplay.displayVoteGuide()
			
	def showActionVoteStatic(self, numbersToDraw: list[int]) -> None:
		logger.info(f"showActionVoteStatic numbersToDraw: {numbersToDraw}")
		self.lastDrawnActionNumbers = numbersToDraw
		voteDisplay: ActionVoteDisplay
		for i in numbersToDraw:
			if i < 1 or i > 8:	
				continue
			voteDisplay = self.itemActionVoteDisplays[i]
			voteDisplay.displayVoteGuide()

	def drawActionVotes(self, actionVotes: list[VotingTallyEntry], adrenalineItemVotes: list[VotingTallyEntry]) -> None:
		logger.info(f"drawActionVotes. lastDrawnActionNumbers -> {self.lastDrawnActionNumbers}, len actionVotes: {len(actionVotes)}")
		noVoteDisplays: list[ActionVoteDisplay] = list[ActionVoteDisplay]()
		noVoteDisplays.extend(list(self.itemActionVoteDisplays.values()))
		noVoteDisplays.extend(list(self.shootActionVoteDisplays.values()))
		
		tallyEntry: VotingTallyEntry
		for tallyEntry in actionVotes:
			voteObj: Vote = tallyEntry.getVoteObj()
			vote: Action = voteObj.getVote()
			if type(vote) is UseItemAction:
				if vote.getItemNum() not in self.lastDrawnActionNumbers:
					continue
				voteDisplay: ActionVoteDisplay = self.itemActionVoteDisplays[vote.getItemNum()]
				voteDisplay.displayVote(tallyEntry)
				noVoteDisplays.remove(voteDisplay)
			elif type(vote) is ShootAction:
				voteDisplay: ActionVoteDisplay = self.shootActionVoteDisplays[vote.getTarget()]
				voteDisplay.displayVote(tallyEntry)
				noVoteDisplays.remove(voteDisplay)
		logger.debug(f"Unvoted for: {noVoteDisplays}")
		noVoteDisplay: ActionVoteDisplay
		for noVoteDisplay in noVoteDisplays:
			if type(noVoteDisplay) is ItemActionVoteDisplay:
				if noVoteDisplay.getActionGuide() not in self.lastDrawnActionNumbers:
					logger.debug(f"Skipping unvoted action {noVoteDisplay.getActionGuide()} because it was not drawn previously")
					continue
			noVoteDisplay.displayVote(None)
			
		for i in range(0, 8): #[0, 9)
			logger.debug(f"Accessing index {i} for votes and {i + 1} for displays")
			adrenalineItemVote = adrenalineItemVotes[i] #0 indexed
			logger.debug(f"Vote for {i+1}: {str(adrenalineItemVote)}. Str: {adrenalineItemVote.getVoteStr()}. Num Votes: {adrenalineItemVote.getNumVotes()}")
			voteDisplay = self.dealerItemVoteDisplays[i + 1] #1 indexed
			if adrenalineItemVote.getNumVotes() < 1:
				voteDisplay.clearVoteStats()
			else:
				voteDisplay.displayVote(adrenalineItemVote)

	def clearActionVotes(self) -> None:
		self.canvas.itemconfigure(Tags.ACTION_VOTE_STATS, text="")