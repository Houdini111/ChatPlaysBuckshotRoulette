from ast import List
from email import header
import logging
import math
import json
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QColorConstants
from PyQt5.QtCore import Qt
from abc import ABC, abstractmethod
from typing import Callable

from .OutlinedLabel import OutlinedLabel
from shared.util import resizeXFrom1440p, resizeYFrom1440p, flagValueInFlag
from shared.consts import nameLeaderboardCount
from bot.vote import VotingTallyEntry

logger = logging.getLogger(__name__)

class LeaderboardWidget():
	def __init__(self, x1440: int, y1440: int, headerText: str, createLabel: Callable, parent, h1440: int = -1, w1440: int = -1, lineSpacingFactor = 0.1, maxChildren: int = -1, baseFontSize: int = 80, childFontFactor = 0.75, alignment: Qt.Alignment | Qt.AlignmentFlag = Qt.AlignTop | Qt.AlignLeft, largestExpectedText: str = None):
		self.name = headerText
		
		self.widgetRoot: QtWidgets.QFrame = QtWidgets.QFrame()
		self.layoutRoot = QtWidgets.QVBoxLayout()
		self.widgetRoot.setLayout(self.layoutRoot)
		self.parent = parent
		self.widgetRoot.setParent(self.parent)
		if maxChildren == -1:
			maxChildren = nameLeaderboardCount
		elif maxChildren > nameLeaderboardCount:
			maxChildren = nameLeaderboardCount
		self.max_children = maxChildren
		
		#TODO: Make config to show
		self.widgetRoot.setLineWidth(5)
		self.widgetRoot.setMidLineWidth(5)
		self.widgetRoot.setFrameStyle(QtWidgets.QFrame.Shape.Box)
		self.widgetRoot.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
		
		
		self.init_elements(headerText, createLabel, baseFontSize, childFontFactor, alignment)

		(hReal, wReal) = self.calculate_size(h1440, w1440, lineSpacingFactor, headerText, largestExpectedText)

		xReal: int = resizeXFrom1440p(x1440)
		yReal: int = resizeYFrom1440p(y1440)

		xFinal: int = xReal #Assumes left aligned
		yFinal: int = yReal #Assumes top aligned
		
		#TODO: This + the forcing element alignment to be left top works for headers (somehow) but the lists are left aligned with the right aligned header, causing them to go too far.
		#   Maybe make the children right aligned and the parent left? ¯\_(ツ)_/¯
		if flagValueInFlag(Qt.AlignmentFlag.AlignRight, alignment):
			logger.debug(f"Leaderboard \"{self.name}\" shifting left by {wReal} 1440p pixels because it is right aligned")
			xFinal -= wReal
		if flagValueInFlag(Qt.AlignmentFlag.AlignBottom, alignment):
			logger.debug(f"Leaderboard \"{self.name}\" shifting up by {yReal} 1440p pixels because it is bottom aligned")
			yFinal -= hReal

		self.widgetRoot.move(xFinal, yFinal)
		self.widgetRoot.setFixedSize(wReal, hReal)
		logger.debug(f"Leaderboard \"{self.name}\" final position [{xFinal}, {yFinal}] and size [{wReal}, {hReal}]")
		logger.debug(f"Leaderboard \"{self.name}\" final coordinates then are [({xFinal}, {yFinal}), ({xFinal + wReal}, {yFinal}), ({xFinal + wReal}, {yFinal + hReal}), ({xFinal}, {yFinal + hReal})]")
		

	def init_elements(self, headerText: str, createLabel: Callable, baseFontSize: int, childFontFactor: float, alignment: Qt.Alignment | Qt.AlignmentFlag) -> None:
		childFontSize = int(math.ceil(baseFontSize * childFontFactor))

		#alignment = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
		self.header = createLabel(headerText, fontSize= baseFontSize, parent= self.widgetRoot, alignment= alignment)#Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
		headerPos: QtCore.QPoint = self.header.pos()
		logger.debug(f"Header \"{headerText}\" position: ({headerPos.x()}, {headerPos.y()}) Size: ({self.header.width()}, {self.header.height()})")
		alignmentIsLeft = flagValueInFlag(Qt.AlignmentFlag.AlignLeft, alignment)
		alignmentIsRight = flagValueInFlag(Qt.AlignmentFlag.AlignRight, alignment)
		alignmentIsTop = flagValueInFlag(Qt.AlignmentFlag.AlignTop, alignment)
		alignmentIsBottom = flagValueInFlag(Qt.AlignmentFlag.AlignBottom, alignment)
		logger.debug(f"Leaderboard \"{self.name}\" header alignment is [{alignmentIsLeft} <-> {alignmentIsRight}] and [{alignmentIsTop} ^v {alignmentIsBottom}]")
		self.layoutRoot.addWidget(self.header)
		headerBottomMargin: int = int(math.ceil(baseFontSize * 0.5))
		self.layoutRoot.addSpacing(headerBottomMargin)
		self.children = list()
		for i in range(self.max_children):
			child = createLabel(f"", fontSize= childFontSize, parent= self.widgetRoot, alignment= alignment)
			self.children.append(child)
			self.layoutRoot.addWidget(child)
		#Extra spacing to keep away from the bottom
		self.layoutRoot.addSpacing(int(headerBottomMargin/2))
		
	def calculate_size(self, h1440: int, w1440: int, lineSpacingFactor: float, headerText: str, largestExpectedText: str):
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
			if largestExpectedText is None or len(largestExpectedText) < len(headerText):
				largestExpectedText = headerText
			textBaseWidth: int = headerFontMetrics.width(largestExpectedText)
			labelMargin: int = self.header.contentsMargins().left() + self.header.contentsMargins().right()
			layoutMargin: int = self.layoutRoot.contentsMargins().left() + self.layoutRoot.contentsMargins().right()
			widgetMargin: int = self.widgetRoot.contentsMargins().left() + self.widgetRoot.contentsMargins().right()
			wReal = textBaseWidth + labelMargin + layoutMargin + widgetMargin
		else:
			wReal = resizeXFrom1440p(w1440)
			
		return (hReal, wReal)
	
	def set_list_text(self, i: int, text: str) -> None:
		logger.debug(f"LeaderboardWidget \"{self.name}\" seting {i} to {text}")
		if i < 0 or i >= self.max_children:
			return
		self.children[i].setText(text)
		
	def show(self) -> None:
		logger.debug(f"LeaderboardWidget \"{self.name}\" showing")
		self.header.show()
		for child in self.children:
			child.show()
			
	def hide(self) -> None:
		logger.debug(f"LeaderboardWidget \"{self.name}\" hiding")
		self.header.hide()
		for child in self.children:
			child.hide()
		
class Leaderboard(ABC):
	def __init__(self, leaderboardWidget: LeaderboardWidget):
		logger.debug(f"Leaderboard2 \"{leaderboardWidget.name}\" initializing")
		self.leaderboardWidget = leaderboardWidget
		self.lastString = ""
		self.lastHash = -1
		self.lastRowCount = 0
		
	def displayVotes(self, votes: list[VotingTallyEntry]) -> None:
		logger.debug(f"Leaderboard2 \"{self.leaderboardWidget.name}\" displaying {len(votes)} votes")
		newString: str = f"{votes}"
		newHash: int = hash(newString)
		logger.debug(f"Leaderboard2 \"{self.leaderboardWidget.name}\" old hash: {self.lastHash} -> new hash: {newHash}")
		logger.debug(f"Leaderboard2 \"{self.leaderboardWidget.name}\" old string to hash: ||{self.lastString}|| -> new string to hash: ||{newString}||")
		if newHash == self.lastHash:
			return
		
		end: int = min(self.leaderboardWidget.max_children, len(votes))
		logger.debug(f"Leaderboard2 \"{self.leaderboardWidget.name}\" Displaying {end+1} votes for leaderboard because max_children is {self.leaderboardWidget.max_children} and the number of votes is {len(votes)}")
		for i in range(self.leaderboardWidget.max_children):
			if i < end:
				vote: VotingTallyEntry = votes[i]
				voteText: str = self.formatRowText(vote)
				self.leaderboardWidget.set_list_text(i, voteText)
			else:
				self.leaderboardWidget.set_list_text(i, "")
				
		self.lastString = newString
		self.lastHash = newHash
		self.lastRowCount = end
	
	def clearRows(self) -> None:
		logger.debug(f"Leaderboard2 \"{self.leaderboardWidget.name}\" clearing rows")
		if self.lastHash == -1:
			return
		for i in range(self.leaderboardWidget.max_children):
			self.leaderboardWidget.set_list_text(i, "")
		self.lastHash = -1
		
	def show(self) -> None:
		logger.debug(f"Leaderboard2 \"{self.leaderboardWidget.name}\" showing widget")
		self.leaderboardWidget.show()
		
	def hide(self) -> None:
		logger.debug(f"Leaderboard2 \"{self.leaderboardWidget.name}\" hiding widget")
		self.leaderboardWidget.hide()

	@abstractmethod
	def formatRowText(self, tallyEntry: VotingTallyEntry) -> str:
		pass