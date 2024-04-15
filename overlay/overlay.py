import json
import tkinter as tk
from typing import Callable
from PIL import ImageTk, Image
import pyautogui	
from time import sleep
from threading import Thread
import math
from operator import itemgetter
import logging

from shared.util import resizePointFrom1440p
from shared.log import log
from bot.vote import Vote, VotingTally, VotingTallyEntry
from shared.actions import Action, ShootAction, UseItemAction

#TODO: Round number, Double or nothing set number, voting numbers (absolute, percent, bars, pie chart), the names and votes of chatters as they come in?, countdown (including clock?) for voting time

logger = logging.getLogger(__name__ + 'overlay.overlay')

class ActionVoteDisplay():
	def __init__(self, number: int, x1440: int, y1440: int, fontSize: int, draw_text_1440: Callable, canvas: tk.Canvas):
		self.number: int = number
		self.x1440: int = x1440
		self.y1440: int = y1440
		self.fontSize: int = fontSize
		self.canvas: tk.Canvas = canvas
		self.mainTextId: int = draw_text_1440(str(number), x1440, y1440, self.fontSize, textTags = ["actionOverlay"])
		self.statsTextId: int = draw_text_1440("", x1440, y1440 - int(fontSize * 1.5), int(self.fontSize * 0.5), textTags = ["actionOverlay", "voteStats"])
	
	def displayNumber(self) -> None:
		self.canvas.itemconfig(self.mainTextId, state="normal")

	def displayVote(self, voteEntry: VotingTallyEntry | None) -> None:
		numVotesStr: str = "0"
		percentStr: str = "  0%"
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
			1: [650, 500],	
			2: [875, 500],
			3: [1600, 500],
			4: [1825, 500],
			5: [525, 750],
			6: [825, 750],
			7: [1675, 750],
			8: [1950, 750]
		}
		
		self.voteList: list[int] = []
		
		self.voteLeaderboardY = 500
		self.draw_text_1440("Chat Overlay Active", 12, 10, 50)
		self.statusText = self.draw_text_1440("", 12, 10 + int(1.25 * self.optionsFontSize), 40)
		self.initNameLeaderboard()
		self.initActionVotesDisplay()
	
	def run(self) -> None:
		tk.mainloop()
	
	def stop(self) -> None:
		self.root.destroy()

	def draw_text_1440(self, text: str, x1440: int, y1440: int, fontSize: float, bold: bool = True, textTags: list[str] = []) -> int:
		realX, realY = resizePointFrom1440p(x1440, y1440)
		font = ("Arial", fontSize)
		if bold:
			font += ("bold", )
		return self.canvas.create_text(realX, realY, text = text, fill = "white", font = font, anchor = "nw", tags = textTags)

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
		self.nameHeader = self.draw_text_1440("Next Name Ranking", 12, self.voteLeaderboardY, 60)
		#TODO: Scale positions
		y = self.voteLeaderboardY + int(60 * 2.5) #Offset + fontsize
		for i in range(5):
			voteId: int = self.draw_text_1440("", 12, y, 30)
			self.voteList.append(voteId)
			y += 60
	
	def initActionVotesDisplay(self) -> None:
		self.actionVotesDisplays: dict[int, ActionVoteDisplay] = {}
		self.lastDrawnActionNumbers: list[int] = []
		for i in range(1, 9): #[1, 9)
			if i < 1 or i > 8:
				continue
			pos = self.playerNumGridPositions[i]
			#textId: int = self.draw_text_1440(str(i), pos[0], pos[1], self.optionsFontSize, textTags = ["actionOverlay"])
			#self.numberGridTextIds.append(textId)
			voteDisplay: ActionVoteDisplay = ActionVoteDisplay(i, pos[0], pos[1], self.optionsFontSize, self.draw_text_1440, self.canvas)
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
		log(f"drawActionVotes. lastDrawnActionNumbers -> {self.lastDrawnActionNumbers}")
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
				log(f"Skipping unvoted action {unvotedAction} because it was not drawn previously")
				continue
			voteDisplay: ActionVoteDisplay = self.actionVotesDisplays[unvotedAction]
			voteDisplay.displayVote(None)
			
	def clearActionOverlay(self) -> None:
		self.canvas.itemconfigure("actionOverlay", state="hidden")
		self.lastDrawnActionNumbers.clear()
		
	def clearActionVotes(self) -> None:
		self.canvas.itemconfigure("voteStats", text="")
		

overlay: Overlay
def getOverlay() -> Overlay:
	return overlay
