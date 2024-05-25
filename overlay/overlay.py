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
from shared.config import useSidebarActionOverlay
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

	def drawNameVoteLeaderboard(self, votes: list[VotingTallyEntry]) -> None:
		self.clearOldNameLeaderboard()
		self.nameLeaderboard.displayVotes(votes)

	def initNameLeaderboard(self) -> None:
		self.nameLeaderboard: Leaderboard = NameLeaderboard("Next Name Ranking", 5, 20, 950, int(math.ceil(self.baseFontSize*0.85)), self.draw_text_1440, self.canvas)

	def initActionVotesDisplay(self) -> None:
		if useSidebarActionOverlay():
			self.actionVoteDisplay: FullScreenVoteDisplay = FullScreenVoteDisplay(self.baseFontSize, self.draw_text_1440, self.canvas)
		else:
			self.actionVoteDisplay: SidebarVoteDisplay = SidebarVoteDisplay(self.baseFontSize, self.draw_text_1440, self.canvas) 
		self.clearActionOverlay()

	def showActionVoteStatic(self, numbersToDraw: list[int]) -> None:
		logger.info(f"showActionVoteStatic numbersToDraw: {numbersToDraw}")
		self.actionVoteDisplay.showActionVoteStatic(numbersToDraw)

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
