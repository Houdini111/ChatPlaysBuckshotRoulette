import json
import tkinter as tk
from PIL import ImageTk, Image
import pyautogui	
from time import sleep
from threading import Thread
import math
from operator import itemgetter
import logging

from bot.vote import VotingTally, VotingTallyEntry
from shared.util import resizePointFrom1440p
from shared.log import log

#TODO: Round number, Double or nothing set number, voting numbers (absolute, percent, bars, pie chart), the names and votes of chatters as they come in?, countdown (including clock?) for voting time

logger = logging.getLogger(__name__ + 'scripts.overlay')

class ActionVote():
	def __init__(self, x1440: int, y1440: int, fontSize: int, draw_text_1440, canvas: tk.Canvas):
		self.x1440 = x1440
		self.y1440 = y1440
		self.fontSize = fontSize
		self.canvas = canvas
		self.mainTextId = draw_text_1440("", x1440, y1440, self.fontSize, textTags = ["numberGrid"])
		self.statsTextId = draw_text_1440("", x1440, y1440 - int(fontSize * 1.5), textTags = ["numberGrid"])
	
	def displayNumber(self, num: str) -> None:
		self.canvas.itemconfig(self.mainTextId, text=str(num))

	def displayVote(self, voteEntry: VotingTallyEntry) -> None:
		statsText = f"[{voteEntry.getNumVotes()}] ({voteEntry.getPercentageStr()})"
		self.canvas.itemconfig(self.statsTextId, text=statsText)

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
		
		self.numberGridTextIds: list[int] = []
		self.voteList: list[int] = []
		
		self.voteLeaderboardY = 500
		self.draw_text_1440("Chat Overlay Active", 12, 10, 50)
		self.statusText = self.draw_text_1440("", 12, 10 + int(1.25 * self.optionsFontSize), 40)
		self.initNameLeaderboard()
		self.initNumberGrid()
	
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
		
	def clearNumberGrid(self) -> None:
		self.canvas.itemconfigure("numberGrid", state="hidden")

	def drawNumberGrid(self, numbersToDraw: list[int]) -> None:
		self.clearNumberGrid()
		for i in numbersToDraw:
			if i < 1 or i > 8:
				continue
			numberId: int = self.numberGridTextIds[i - 1]
			self.canvas.itemconfigure(numberId, state="normal")
	
	def drawActionVotes(self, actionVotes: list[VotingTallyEntry]) -> None:
		pass
	
	def clearOldNameLeaderboard(self) -> None:
		self.canvas.itemconfig("nameLeaderboard", text="")

	def drawNameVoteLeaderboard(self, votes: list[VotingTallyEntry]) -> None:
		self.clearOldNameLeaderboard()
		for textId, vote in zip(self.voteList, votes):
			voteStr = f"{vote.getVoteStr()} [{vote.getNumVotes()}] ({vote.getPercentageStr()})"
			self.canvas.itemconfig(textId, text = voteStr)
			
	def initNameLeaderboard(self) -> None:
		self.nameHeader = self.draw_text_1440("Top Names", 12, self.voteLeaderboardY, 40)
		#TODO: Scale positions
		y = self.voteLeaderboardY + int(40 * 2.5) #Offset + fontsize
		for i in range(5):
			voteId: int = self.draw_text_1440("", 12, y, 20)
			self.voteList.append(voteId)
			y += 45
	
	def initNumberGrid(self) -> None:
		for i in range(1, 9): #[1, 9)
			if i < 1 or i > 8:
				continue
			pos = self.playerNumGridPositions[i]
			textId: int = self.draw_text_1440(str(i), pos[0], pos[1], self.optionsFontSize, textTags = ["numberGrid"])
			self.numberGridTextIds.append(textId)
		#self.clearNumberGrid()

overlay: Overlay
def getOverlay() -> Overlay:
	return overlay
