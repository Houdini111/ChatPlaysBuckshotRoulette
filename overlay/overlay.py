from abc import abstractmethod
import json
import tkinter as tk
from typing import Callable, Generic, Literal, TypeVar
import pyautogui	
from time import sleep
from threading import Thread
import math
from operator import itemgetter
import logging

from shared.consts import Target
from shared.util import resizePointFrom1440p
from shared.actions import Action, ShootAction, UseItemAction
from bot.vote import Vote, VotingTally, VotingTallyEntry
from .consts import Tags
from .actionVoteDisplay import ActionVoteDisplay
from .fullScreenVoteDisplay import FullScreenVoteDisplay
from .sidebarVoteDisplay import SidebarVoteDisplay
from .leaderboard import Leaderboard
from .voteActionLeaderboard import VoteActionLeaderboard
from .nameLeaderboard import NameLeaderboard

#TODO: Round number, Double or nothing set number, voting numbers (absolute, percent, bars, pie chart), the names and votes of chatters as they come in?, countdown (including clock?) for voting time

logger = logging.getLogger(__name__)


ActionVoteType = TypeVar("ActionVoteType", int, Target)

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
		
		self.statusText = self.draw_text_1440("", 20, 20, int(self.baseFontSize*50/80), self.canvas)
		self.initNameLeaderboard()
		self.initActionVotesDisplay()
		
		#self.voteActionLeaderboard: Leaderboard = VoteActionLeaderboard("Test Header", 5, 1080, 420, 50, self.draw_text_1440, self.canvas)
	
	def run(self) -> None:
		tk.mainloop()
	
	def stop(self) -> None:
		self.root.destroy()

	def draw_text_1440(self, text: str, x1440: int, y1440: int, fontSize: float, canvas: tk.Canvas, bold: bool = True, textTags: list[str] = list[str](), anchor: str = "nw") -> int:
		realX, realY = resizePointFrom1440p(x1440, y1440)
		#font = ("Arial", fontSize)
		font = ("Lucida Console", fontSize) #I really want a cleaner monospace font included in windows...
		if bold:
			font += ("bold", )
		logger.debug(f"Drawing text [[{text}]] at 1440 coordinates [{x1440}, {y1440}] with the font {font}, the tags {textTags} and the anchor {anchor}")
		return canvas.create_text(realX, realY, text = text, fill = "white", font = font, anchor = anchor, tags = textTags) # type: ignore (doesn't like the anchor parameter)

	def updateStatusText(self, text: str) -> None:
		self.canvas.itemconfigure(self.statusText, text=text)
	
	def clearOldNameLeaderboard(self) -> None:
		logger.info("Clearing old name leaderboard")
		self.nameLeaderboard.clearRows()

	def oldClearOldNameLeaderboard(self) -> None:
		logger.info("Clearing old name leaderboard")
		self.canvas.itemconfig(Tags.NAME_LEADERBOARD, text="")

	def drawNameVoteLeaderboard(self, votes: list[VotingTallyEntry]) -> None:
		self.clearOldNameLeaderboard()
		self.nameLeaderboard.displayVotes(votes)

	def oldDrawNameVoteLeaderboard(self, votes: list[VotingTallyEntry]) -> None:
		self.clearOldNameLeaderboard()
		for textId, vote in zip(self.voteList, votes):
			namePadding = " " * (6 - len(vote.getVoteStr()))
			numPadding = " " * (3 - len(str(vote.getNumVotes()))) #I doubt this bot is ever going to see >999. If it does then it'll screw up the spacing. Oh no. 
			voteStr = f"{vote.getVoteStr()}{namePadding} {numPadding}[{vote.getNumVotes()}] ({vote.getPercentageStr()})"
			logger.debug(f"Drawing leaderboard name:  {voteStr}")
			self.canvas.itemconfig(textId, text = voteStr)
			
	def initNameLeaderboard(self) -> None:
		#self.initOldNameLeaderboard()
		self.nameLeaderboard: Leaderboard = NameLeaderboard("Next Name Ranking", 5, 20, 950, int(math.ceil(self.baseFontSize*0.85)), self.draw_text_1440, self.canvas)

	def initOldNameLeaderboard(self) -> None:
		nameLeaderboardY = 1050

		headerFontSize = int(self.baseFontSize/4)
		self.nameHeader = self.draw_text_1440("Next Name Ranking", 10, nameLeaderboardY, 60, self.canvas, anchor = "sw")
		nameLeaderboardItemFontSize = int(self.baseFontSize*45/80)
		y = nameLeaderboardY + int(headerFontSize * .1)
		yInc = int(nameLeaderboardItemFontSize * 1.75)
		for i in range(5):
			voteId: int = self.draw_text_1440("", 20, y, nameLeaderboardItemFontSize, self.canvas, textTags = [Tags.NAME_LEADERBOARD], anchor = "nw")
			self.voteList.append(voteId)
			y += yInc
	
	def initActionVotesDisplay(self) -> None:
		#TODO: Config value and sidebarVoteDisplay
		if True:
			self.actionVoteDisplay: ActionVoteDisplay = FullScreenVoteDisplay(self.baseFontSize, self.draw_text_1440, self.canvas)
		else:
			self.actionVoteDisplay: ActionVoteDisplay = SidebarVoteDisplay(self.baseFontSize, self.draw_text_1440, self.canvas) 
		self.clearActionOverlay()

	def showActionVoteStatic(self, numbersToDraw: list[int]) -> None:
		logger.info(f"showActionVoteStatic numbersToDraw: {numbersToDraw}")
		self.actionVoteDisplay.showActionVoteStatic(numbersToDraw)
			
	#TODO: Remove?
	def displayItemActionGuides(self, numbersToDraw: list[int]) -> None:
		logger.info(f"displayItemActionGuides numbersToDraw: {numbersToDraw}")
		self.lastDrawnActionNumbers = numbersToDraw
		voteDisplay: ActionVoteDisplay
		for i in numbersToDraw:
			if i < 1 or i > 8:	
				continue
			voteDisplay = self.itemActionVoteDisplays[i]
			voteDisplay.displayVoteGuide()

	def drawActionVotes(self, actionVotes: list[VotingTallyEntry], adrenalineItemVotes: list[VotingTallyEntry]) -> None:
		logger.info(f"drawActionVotes. lastDrawnActionNumbers -> {self.lastDrawnActionNumbers}, len actionVotes: {len(actionVotes)}")
		self.actionVoteDisplay.drawActionVotes(actionVotes, adrenalineItemVotes)
			
	def clearActionOverlay(self) -> None:
		self.clearActionVotes()
		self.clearActionVoteStatic()

	def clearActionVoteStatic(self) -> None:
		self.canvas.itemconfigure(Tags.ACTION_VOTE_STATIC, state="hidden")
		self.lastDrawnActionNumbers = list[int]()
		
	def clearActionVotes(self) -> None:
		self.canvas.itemconfigure(Tags.ACTION_VOTE_STATS, text="")
		

overlay: Overlay
def getOverlay() -> Overlay:
	return overlay
