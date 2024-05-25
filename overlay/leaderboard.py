from abc import ABC, abstractmethod
from typing import Callable
import tkinter as tk
import logging
import math

from bot.vote import VotingTallyEntry

logger = logging.getLogger(__name__)

class Leaderboard(ABC):
	def __init__(self, header: str, maxLen: int, x1440: int, y1440: int, baseFontSize: int, draw_text_1440: Callable, canvas: tk.Canvas, anchor: str = "nw") -> None:
		self.canvas = canvas
		self.maxLen = maxLen
		#TODO: Make these configurable per leaderboard
		self.rowSize = 0.75
		self.lineSpacing = 1.5
		
		self.header = draw_text_1440(header, x1440, y1440, baseFontSize, canvas, anchor = anchor, textTags = self.getHeaderTags())
		firstRowOffset: int = int(math.ceil(self.lineSpacing * baseFontSize))
		self.initBoardRows(x1440, y1440 + firstRowOffset, baseFontSize, anchor, draw_text_1440)
		
	def initBoardRows(self, x1440: int, y1440: int, baseFontSize: int, anchor: str, draw_text_1440: Callable) -> None:
		myFontSize: int = int(math.ceil(self.rowSize * baseFontSize))
		rowOffset: int = int(math.ceil(self.lineSpacing * myFontSize))
		nextRowY: int = y1440 
		self.boardRowText: list[int] = list[int]()
		while len(self.boardRowText) < self.maxLen:
			newRow: int = draw_text_1440("", x1440, nextRowY, myFontSize, self.canvas, anchor = anchor, textTags = self.getBoardRowTags())
			nextRowY += rowOffset
			self.boardRowText.append(newRow)

	def hide(self) -> None:
		self.hideHeader()
		self.hideRows()
	
	def showHeader(self) -> None:
		self.canvas.itemconfig(self.header, state="normal")
		
	def hideHeader(self) -> None:
		self.canvas.itemconfig(self.header, state="hidden")

	def hideRows(self) -> None:
		self.canvas.itemconfig(self.getBoardRowTags, state="hidden")
	
	def clearRows(self) -> None:
		#TODO: NAME LEADERBOARD DIDN'T CLEAR
		self.canvas.itemconfig(self.getBoardRowTags, text="")
			
	def displayVotes(self, votes: list[VotingTallyEntry]) -> None:
		for i in range(len(votes)):
			self.displayVote(i, votes[i])

	def displayVote(self, i: int, vote: VotingTallyEntry) -> None:
		self.canvas.itemconfig(self.boardRowText[i], text = self.formatRowText(vote))

	@abstractmethod	
	def getHeaderTags(self) -> list[str]:
		pass

	@abstractmethod	
	def getBoardRowTags(self) -> list[str]:
		pass

	@abstractmethod
	def formatRowText(self, tallyEntry: VotingTallyEntry) -> str:
		pass