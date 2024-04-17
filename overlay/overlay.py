from abc import abstractmethod
import json
import tkinter as tk
from typing import Callable, Generic, Literal, TypeVar
from PIL import ImageTk, Image
import pyautogui	
from time import sleep
from threading import Thread
import math
from operator import itemgetter
import logging
from shared.consts import Target

from shared.util import resizePointFrom1440p
from shared.log import log
from shared.actions import Action, ShootAction, UseItemAction
from bot.vote import Vote, VotingTally, VotingTallyEntry

#TODO: Round number, Double or nothing set number, voting numbers (absolute, percent, bars, pie chart), the names and votes of chatters as they come in?, countdown (including clock?) for voting time

logger = logging.getLogger(__name__ + 'overlay.overlay')

ActionVoteType = TypeVar("ActionVoteType", int, Target)

class ActionVoteDisplay(Generic[ActionVoteType]):
	def __init__(self, actionGuide: ActionVoteType, x1440: int, y1440: int, fontSize: int, draw_text_1440: Callable, canvas: tk.Canvas):
		self.actionGuide: ActionVoteType = actionGuide
		self.x1440: int = x1440
		self.y1440: int = y1440
		self.fontSize: int = fontSize
		self.canvas: tk.Canvas = canvas
		self.mainTextId: int = draw_text_1440(str(actionGuide), x1440, y1440, self.fontSize, textTags = ["actionOverlay"], anchor = "center")
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
		if type(actionGuide) is Target:
			logger.debug("Action guide is for Targets")
			if actionGuide == Target.DEALER:
				logger.debug("Action guide is for Target DEALER")
				verticalOffset = verticalOffset * -1
		logger.debug(f"Vertical offset for actionGuide: {actionGuide} is {verticalOffset}")
		self.statsTextId: int = draw_text_1440("", x1440 + horizontalOffset, y1440 - verticalOffset, int(self.fontSize * 0.5), textTags = ["actionOverlay", "voteStats"], anchor = anchor)
	
	def getActionGuide(self) -> ActionVoteType:
		return self.actionGuide

	def displayVoteGuide(self) -> None:
		logger.debug(f"Displaying vote guide for {self.actionGuide}")
		self.canvas.itemconfig(self.mainTextId, state="normal")

	def displayVote(self, voteEntry: VotingTallyEntry | None) -> None:
		logger.debug(f"Displaying vote for vote guide {self.actionGuide}. Vote: {voteEntry}")
		numVotesStr: str = "0"
		percentStr: str = "0%"
		if voteEntry is not None:
			numVotesStr = str(voteEntry.getNumVotes())
			percentStr = voteEntry.getPercentageStr()
		statsText = f"{numVotesStr} ({percentStr})"
		self.canvas.itemconfig(self.statsTextId, text=statsText)
		self.canvas.itemconfig(self.statsTextId, state="normal")
		
class ItemActionVoteDisplay(ActionVoteDisplay):
	pass

class ShootActionVoteDisplay(ActionVoteDisplay):
	pass

class Overlay():
	def __init__(self):
		global overlay
		overlay = self
		self.displayW, self.displayH = pyautogui.size()
		self.root: tk.Tk = tk.Tk()
		self.root.title("Chat Plays Buckshot Roulette - Chat Overlay")
		self.root.wm_attributes("-fullscreen", True)
		self.root.wm_attributes("-transparentcolor", "green")

		self.canvas = tk.Canvas(width = self.displayW, height = self.displayH, bg="green")
		self.canvas.pack(expand=tk.YES, fill=tk.BOTH)
		
		self.baseFontSize = math.ceil(80 * (float(self.displayH) / 1440)) #80 is the size I want at 1440p
		
		self.voteList: list[int] = []
		
		self.voteLeaderboardY = 1000
		#self.draw_text_1440("Chat Overlay Active", 12, 10, 50)
		#self.statusText = self.draw_text_1440("", 12, 10 + int(1.25 * self.optionsFontSize), 40)
		self.statusText = self.draw_text_1440("", 20, 20, 50)
		self.initNameLeaderboard()
		self.initActionVotesDisplay()
		self.canvas.itemconfigure("nameLeaderboard", state="hidden")
	
	def run(self) -> None:
		tk.mainloop()
	
	def stop(self) -> None:
		self.root.destroy()

	def draw_text_1440(self, text: str, x1440: int, y1440: int, fontSize: float, bold: bool = True, textTags: list[str] = [], anchor: str = "nw") -> int:
		realX, realY = resizePointFrom1440p(x1440, y1440)
		font = ("Arial", fontSize)
		if bold:
			font += ("bold", )
		return self.canvas.create_text(realX, realY, text = text, fill = "white", font = font, anchor = anchor, tags = textTags) # type: ignore (doesn't like the anchor parameter)

	def updateStatusText(self, text: str) -> None:
		self.canvas.itemconfigure(self.statusText, text=text)
	
	def clearOldNameLeaderboard(self) -> None:
		log("Clearing old name leaderboard")
		self.canvas.itemconfig("nameLeaderboard", text="")

	def drawNameVoteLeaderboard(self, votes: list[VotingTallyEntry]) -> None:
		self.clearOldNameLeaderboard()
		for textId, vote in zip(self.voteList, votes):
			voteStr = f"{vote.getVoteStr()} [{vote.getNumVotes()}] ({vote.getPercentageStr()})"
			self.canvas.itemconfig(textId, text = voteStr)
			
	def initNameLeaderboard(self) -> None:
		self.nameHeader = self.draw_text_1440("Next Name Ranking", 20, self.voteLeaderboardY, 60)
		#TODO: Scale positions
		y = self.voteLeaderboardY + int(60 * 1.75) #Offset + fontsize
		for i in range(5):
			voteId: int = self.draw_text_1440("", 20, y, 35, textTags = ["nameLeaderboard"])
			self.voteList.append(voteId)
			y += 65
	
	def initActionVotesDisplay(self) -> None:
		self.itemActionVoteDisplays: dict[int, ItemActionVoteDisplay] = dict[int, ItemActionVoteDisplay]()
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
			voteDisplay = ItemActionVoteDisplay(i, pos[0], pos[1], numberFontSize, self.draw_text_1440, self.canvas)
			self.itemActionVoteDisplays[i] = voteDisplay
		self.shootActionVoteDisplays: dict[Target, ShootActionVoteDisplay] =  dict[Target, ShootActionVoteDisplay]()
		voteDisplay = ShootActionVoteDisplay(Target.DEALER, int(2560/2), self.baseFontSize, self.baseFontSize, self.draw_text_1440, self.canvas)
		self.shootActionVoteDisplays[Target.DEALER] = voteDisplay
		voteDisplay = ShootActionVoteDisplay(Target.SELF, int(2560/2), 1440 - self.baseFontSize, self.baseFontSize, self.draw_text_1440, self.canvas)
		self.shootActionVoteDisplays[Target.SELF] = voteDisplay
		self.clearActionOverlay()
		
	def showActionVotes(self, numbersToDraw: list[int]) -> None:
		log(f"showActionVotes numbersToDraw: {numbersToDraw}")
		self.clearActionOverlay()
		self.displayItemActionGuides(numbersToDraw)
			
	def displayItemActionGuides(self, numbersToDraw: list[int]) -> None:
		log(f"displayItemActionGuides numbersToDraw: {numbersToDraw}")
		self.lastDrawnActionNumbers = numbersToDraw
		voteDisplay: ActionVoteDisplay
		for i in numbersToDraw:
			if i < 1 or i > 8:	
				continue
			voteDisplay = self.itemActionVoteDisplays[i]
			voteDisplay.displayVoteGuide()
	
	def displayShootActionGuides(self) -> None:
		log("displayShootActionGuides")
		voteDisplay: ActionVoteDisplay
		for voteDisplay in self.shootActionVoteDisplays.values():
			voteDisplay.displayVoteGuide()

	def drawActionVotes(self, actionVotes: list[VotingTallyEntry]) -> None:
		log(f"drawActionVotes. lastDrawnActionNumbers -> {self.lastDrawnActionNumbers}, len actionVotes: {len(actionVotes)}", logLevel= logging.DEBUG)
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
		log(f"Unvoted for: {noVoteDisplays}")
		noVoteDisplay: ActionVoteDisplay
		for noVoteDisplay in noVoteDisplays:
			if type(noVoteDisplay) is ItemActionVoteDisplay:
				if noVoteDisplay.getActionGuide() not in self.lastDrawnActionNumbers:
					log(f"Skipping unvoted action {noVoteDisplay.getActionGuide()} because it was not drawn previously", logLevel= logging.DEBUG)
					continue
			noVoteDisplay.displayVote(None)
			
	def clearActionOverlay(self) -> None:
		self.canvas.itemconfigure("actionOverlay", state="hidden")
		self.lastDrawnActionNumbers = list[int]()
		#self.lastDrawnActionNumbers.clear()
		pass
		
	def clearActionVotes(self) -> None:
		self.canvas.itemconfigure("voteStats", text="")
		

overlay: Overlay
def getOverlay() -> Overlay:
	return overlay
