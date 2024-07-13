import logging
import math
import json
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QColorConstants
from PyQt5.QtCore import Qt
from abc import ABC, abstractmethod
from typing import Callable

from .OutlinedLabel import OutlinedLabel
from shared.util import resizePointArrFrom1440p, Point, resizeXFrom1440p, resizeYFrom1440p
from shared.consts import nameLeaderboardCount
from bot.vote import VotingTallyEntry

logger = logging.getLogger(__name__)

class LeaderboardWidget():
	def __init__(self, x1440: int, y1440: int, headerText: str, createLabel: Callable, parent, h1440: int = -1, w1440: int = -1, lineSpacingFactor = 0.1, maxChildren: int = -1, baseFontSize: int = 80, childFontFactor = 0.75, alignment: Qt.Alignment | Qt.AlignmentFlag = Qt.AlignTop | Qt.AlignLeft):
		self.widgetRoot = QtWidgets.QWidget()
		self.layoutRoot = QtWidgets.QVBoxLayout()
		self.widgetRoot.setLayout(self.layoutRoot)
		self.parent = parent
		self.widgetRoot.setParent(self.parent)
		if maxChildren == -1:
			maxChildren = nameLeaderboardCount
		elif maxChildren > nameLeaderboardCount:
			maxChildren = nameLeaderboardCount
		self.max_children = maxChildren
		
		self.init_elements(headerText, createLabel, baseFontSize, childFontFactor, alignment)

		(hReal, wReal) = self.calculate_size(h1440, w1440, lineSpacingFactor, headerText)

		self.widgetRoot.move(x1440, y1440)
		self.widgetRoot.setFixedSize(wReal, hReal)

	def init_elements(self, headerText: str, createLabel: Callable, baseFontSize: int, childFontFactor: float, alignment: Qt.Alignment | Qt.AlignmentFlag) -> None:
		childFontSize = int(math.ceil(baseFontSize * childFontFactor))

		self.header = createLabel(headerText, fontSize= baseFontSize, parent= self.layoutRoot, alignment= alignment)
		self.layoutRoot.addWidget(self.header)
		headerBottomMargin: int = int(math.ceil(baseFontSize * 0.5))
		self.layoutRoot.addSpacing(headerBottomMargin)
		self.children = []
		for i in range(self.max_children):
			child = createLabel(f"", fontSize= childFontSize, parent= self.layoutRoot, alignment= alignment)
			self.children.append(child)
			self.layoutRoot.addWidget(child)
		#Extra spacing to keep away from the bottom
		self.layoutRoot.addSpacing(int(headerBottomMargin/2))
		
	def calculate_size(self, h1440: int, w1440: int, lineSpacingFactor: float, headerText: str):
		headerFontMetrics: QtGui.QFontMetrics = self.header.fontMetrics()
		childFontMetrics: QtGui.QFontMetrics = self.children[0].fontMetrics()
		hReal = 1
		if h1440 == -1:
			headerFontHeight: int = headerFontMetrics.height()
			childFontHeight: int = childFontMetrics.height()
			headerTotalHeight: int = int(math.ceil(headerFontHeight * (1 + lineSpacingFactor)))
			childTotalHeight: int = int(math.ceil(childFontHeight * (1 + lineSpacingFactor)))
			allChildrenHeight: int = childTotalHeight * self.max_children
			hReal = headerTotalHeight + allChildrenHeight
		else:
			hReal = resizeYFrom1440p(h1440)
			
		wReal = 1
		if w1440 == -1:
			textBaseWidth: int = headerFontMetrics.width(headerText)
			labelMargin: int = self.header.contentsMargins().left() + self.header.contentsMargins().right()
			layoutMargin: int = self.layoutRoot.contentsMargins().left() + self.layoutRoot.contentsMargins().right()
			widgetMargin: int = self.widgetRoot.contentsMargins().left() + self.widgetRoot.contentsMargins().right()
			wReal = textBaseWidth + labelMargin + layoutMargin + widgetMargin
		else:
			wReal = resizeXFrom1440p(w1440)
			
		return (hReal, wReal)
	
	def set_list_text(self, i: int, text: str) -> None:
		if i < 0 or i >= self.max_children:
			return
		self.children[i].setText(text)
		
class Leaderboard(ABC):
	def __init__(self, leaderboardWidget: LeaderboardWidget):
		self.leaderboardWidget = leaderboardWidget
		self.lastHash = -1
		
	def displayVotes(self, votes: list[VotingTallyEntry]) -> None:
		newHash: int = hash(f"{votes}")
		logger.debug(f"Leaderboard old hash: {self.lastHash} -> new hash: {newHash}")
		if newHash == self.lastHash:
			return
		self.clearRows()
		end: int = min(self.leaderboardWidget.max_children, len(votes))
		logger.debug(f"Displaying {end+1} votes for leaderboard because max_children is {self.leaderboardWidget.max_children} and the number of votes is {len(votes)}")
		for i in range(end):
			vote: VotingTallyEntry = votes[i]
			voteText: str = self.formatRowText(vote)
			self.leaderboardWidget.set_list_text(i, voteText)
		self.lastHash = newHash
	
	def clearRows(self) -> None:
		if self.lastHash == -1:
			return
		for i in range(self.leaderboardWidget.max_children):
			self.leaderboardWidget.set_list_text(i, "")
		self.lastHash = -1
		
	@abstractmethod
	def formatRowText(self, tallyEntry: VotingTallyEntry) -> str:
		pass