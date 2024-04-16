import json
import tkinter as tk
from typing import Callable, Literal
from PIL import ImageTk, Image
import pyautogui	
from time import sleep
from threading import Thread
import math
from operator import itemgetter
import logging

from shared.util import resizePointFrom1440p
from shared.log import log
from shared.actions import Action, ShootAction, UseItemAction
from bot.vote import Vote, VotingTally, VotingTallyEntry

#TODO: Round number, Double or nothing set number, voting numbers (absolute, percent, bars, pie chart), the names and votes of chatters as they come in?, countdown (including clock?) for voting time

logger = logging.getLogger(__name__ + 'overlay.overlay')

class ActionVoteDisplay():
	def __init__(self, number: int, x1440: int, y1440: int, fontSize: int, draw_text_1440: Callable, canvas: tk.Canvas):
		self.number: int = number
		self.x1440: int = x1440
		self.y1440: int = y1440
		self.fontSize: int = fontSize
		self.canvas: tk.Canvas = canvas
		self.mainTextId: int = draw_text_1440(str(number), x1440, y1440, self.fontSize, textTags = ["actionOverlay"], anchor = "center")
		horizontalOffset: int 
		anchor: str 
		if number % 2 == 0: #Even goes right, so anchor left
			anchor = "w"
			horizontalOffset = -60 #Also move the top numbers closer, so they're not quite so far off their root number
		else: #Odd goes left, so anchor right
			anchor = "e"
			horizontalOffset = 60 
		self.statsTextId: int = draw_text_1440("", x1440 + horizontalOffset, y1440 - int(fontSize * 1.5), int(self.fontSize * 0.5), textTags = ["actionOverlay", "voteStats"], anchor = anchor)
	
	def displayNumber(self) -> None:
		self.canvas.itemconfig(self.mainTextId, state="normal")

	def displayVote(self, voteEntry: VotingTallyEntry | None) -> None:
		numVotesStr: str = "0"
		percentStr: str = "0%"
		if voteEntry is not None:
			numVotesStr = str(voteEntry.getNumVotes())
			percentStr = voteEntry.getPercentageStr()
		statsText = f"{numVotesStr} ({percentStr})"
		self.canvas.itemconfig(self.statsTextId, text=statsText)
		self.canvas.itemconfig(self.statsTextId, state="normal")

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
		
		self.optionsFontSize = math.ceil(80 * (float(self.displayH) / 1440)) #80 is the size I want at 1440p
		
		self.playerNumGridPositions = {
			1: [725, 550],	
			2: [925, 550],
			3: [1625, 550],
			4: [1850, 550],
			5: [550, 900],
			6: [850, 900],
			7: [1700, 900],
			8: [1975, 900]
		}
		
		self.voteList: list[int] = []
		
		self.voteLeaderboardY = 1000
		#self.draw_text_1440("Chat Overlay Active", 12, 10, 50)
		#self.statusText = self.draw_text_1440("", 12, 10 + int(1.25 * self.optionsFontSize), 40)
		self.statusText = self.draw_text_1440("", 20, 20, 50)
		self.initNameLeaderboard()
		self.initActionVotesDisplay()
	
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
		self.actionVotesDisplays: dict[int, ActionVoteDisplay] = dict[int, ActionVoteDisplay]()
		self.lastDrawnActionNumbers: list[int] = list[int]()
		for i in range(1, 9): #[1, 9)
			if i < 1 or i > 8:
				continue
			pos = self.playerNumGridPositions[i]
			voteDisplay: ActionVoteDisplay = ActionVoteDisplay(i, pos[0], pos[1], int(self.optionsFontSize*1.2), self.draw_text_1440, self.canvas)
			self.actionVotesDisplays[i] = voteDisplay
		self.clearActionOverlay()
		
	def drawNumberGrid(self, numbersToDraw: list[int]) -> None:
		log("drawNumberGrid")
		self.clearActionOverlay()
		self.lastDrawnActionNumbers = numbersToDraw
		for i in numbersToDraw:
			if i < 1 or i > 8:	
				continue
			voteDisplay: ActionVoteDisplay = self.actionVotesDisplays[i]
			voteDisplay.displayNumber()
			
	def drawActionVotes(self, actionVotes: list[VotingTallyEntry]) -> None:
		log(f"drawActionVotes. lastDrawnActionNumbers -> {self.lastDrawnActionNumbers}, len actionVotes: {len(actionVotes)}", logLevel= logging.DEBUG)
		unvotedActions: list[int] = list(range(1, 9)) #[1, 9)
		tallyEntry: VotingTallyEntry
		for tallyEntry in actionVotes:
			voteObj: Vote = tallyEntry.getVoteObj()
			vote: Action = voteObj.getVote()
			if type(vote) is UseItemAction:
				if vote.getItemNum() not in self.lastDrawnActionNumbers:
					continue
				voteDisplay: ActionVoteDisplay = self.actionVotesDisplays[vote.getItemNum()]
				voteDisplay.displayVote(tallyEntry)
				unvotedActions.remove(vote.getItemNum())
			elif type(vote) is ShootAction:
				pass #TODO: 
		log(f"Unvoted for: {unvotedActions}")
		for unvotedAction in unvotedActions:
			if unvotedAction not in self.lastDrawnActionNumbers:
				log(f"Skipping unvoted action {unvotedAction} because it was not drawn previously", logLevel= logging.DEBUG)
				continue
			voteDisplay: ActionVoteDisplay = self.actionVotesDisplays[unvotedAction]
			voteDisplay.displayVote(None)
			
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
