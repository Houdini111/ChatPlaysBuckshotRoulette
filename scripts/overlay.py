import json
import tkinter as tk
from PIL import ImageTk, Image
import pyautogui
from time import sleep
from threading import Thread
import math
from operator import itemgetter

from .util import resizePointFrom1440p

#TODO: Round number, Double or nothing set number, voting numbers (absolute, percent, bars, pie chart), the names and votes of chatters as they come in?, countdown (including clock?) for voting time



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
		
		self.numberGridTextIds = []
		self.voteList = []
		
		self.voteLeaderboardY = 400
		self.draw_text_1440("Chat Overlay Active", 12, 10, 40)
		self.statusText = self.draw_text_1440("", 0, 0, 0)
		self.nameHeader = self.draw_text_1440("Top names", 12, self.voteLeaderboardY, 40)
	
	def run(self) -> None:
		tk.mainloop()
	
	def stop(self) -> None:
		self.root.destroy()

	def draw_text_1440(self, text: str, x1440: int, y1440: int, fontSize: float, bold: bool = True) -> int:
		realX, realY = resizePointFrom1440p(x1440, y1440)
		font = ("Arial", fontSize)
		if bold:
			font += ("bold", )
		return self.canvas.create_text(realX, realY, text = text, fill = "white", font = font, anchor = "nw")

	def updateStatusText(self, text: str) -> None:
		self.canvas.delete(self.statusText)
		self.statusText = self.draw_text_1440(text, 12, 70, 40)
		
	def clearNumberGrid(self) -> None:
		if len(self.numberGridTextIds) == 0:
			return
		for textId in self.numberGridTextIds:
			self.canvas.delete(textId)

	def drawNumberGrid(self, numbersToDraw: list[int]) -> None:
		self.clearNumberGrid()
		for i in numbersToDraw:
			if i < 1 or i > 8:
				continue
			pos = self.playerNumGridPositions[i]
			textId = self.draw_text_1440(str(i), pos[0], pos[1], self.optionsFontSize)
			self.numberGridTextIds.append(textId)
	
	def clearOldNameLeaderboard(self) -> None:
		for oldVote in self.voteList:
			self.canvas.delete(oldVote)
		self.voteList.clear()
		
	def 

	def drawNameVoteLeaderboard(self, votes: dict[str, int]) -> None:
		self.clearOldNameLeaderboard()
		sortedVotes = sorted(votes.items(), key=lambda kv: kv[1])
		print(f"Sorted votes: {json.dumps(sortedVotes)}")
		y = self.voteLeaderboardY + 40 #Offset + fontsize
		for vote in sortedVotes:
			voteId = self.draw_text_1440(, 12, y, 20)
			self.voteList.append(voteId)
			y += 40

overlay: Overlay

def getOverlay() -> Overlay:
	return overlay
