from email import header
import sys
import pyautogui
import logging
import math
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QColorConstants
from PyQt5.QtCore import Qt
#from abc import ABC, abstractmethod
from typing import Callable

#from .OutlinedLabel import OutlinedLabel
from OutlinedLabel import OutlinedLabel
#from shared.util import resizePointArrFrom1440p

logger = logging.getLogger(__name__)





#TEMP for running overlay outside the whole system
class Point:
	def __init__(self, x: int, y: int):
		self.x = x
		self.y = y
	
	def __str__(self) -> str:
		return "{" + f"x: {self.x}, y: {self.y}" + "}"

def resizePointArrFrom1440p(x1440: int, y1440: int) -> list[int]:
	return [resizeXFrom1440p(x1440), resizeYFrom1440p(y1440)]

def resizePointFrom1440p(p1440: Point) -> Point:
	return Point(resizeXFrom1440p(p1440.x), resizeYFrom1440p(p1440.y))

def resizeXFrom1440p(x1440: int) -> int:
	xPercent = x1440/2560
	displayW, displayH = pyautogui.size()
	return int(math.ceil(xPercent * displayW))

def resizeYFrom1440p(y1440: int) -> int:
	yPercent = y1440/1440
	displayW, displayH = pyautogui.size()
	return int(math.ceil(yPercent * displayH))
#END TEMP










class LeaderboardWidget():
	def __init__(self, x1440: int, y1440: int, headerText: str, createLabel: Callable, parent, h1440: int = -1, w1440: int = -1, lineSpacingFactor = 0.1, maxChildren: int = 5, baseFontSize: int = 80, childFontFactor = 0.75, alignment: Qt.Alignment | Qt.AlignmentFlag = Qt.AlignTop | Qt.AlignLeft):
		self.widgetRoot = QtWidgets.QWidget()
		self.layoutRoot = QtWidgets.QVBoxLayout()
		self.widgetRoot.setLayout(self.layoutRoot)
		
		self.parent = parent
		self.widgetRoot.setParent(self.parent)
		
		#self.layoutRoot.setContentsMargins(0, 0, 0, 0)
		#self.layoutRoot.setSpacing(0)
		#self.layoutRoot.setSpacing
		
		childFontSize = int(math.ceil(baseFontSize * childFontFactor))

		self.header = createLabel(headerText, fontSize= baseFontSize, parent= self.layoutRoot, alignment= alignment)
		self.layoutRoot.addWidget(self.header)
		
		headerBottomMargin: int = int(math.ceil(baseFontSize * 0.5))
		self.layoutRoot.addSpacing(headerBottomMargin)

		self.children = []
		for i in range(maxChildren):
			child = createLabel(f"Child {i}", fontSize= childFontSize, parent= self.layoutRoot, alignment= alignment)
			self.children.append(child)
			self.layoutRoot.addWidget(child)
			
			
		#Extra spacing to keep away from the bottom
		self.layoutRoot.addSpacing(int(headerBottomMargin/2))
		
		
		headerFontMetrics: QtGui.QFontMetrics = self.header.fontMetrics()
		childFontMetrics: QtGui.QFontMetrics = self.children[0].fontMetrics()
		hReal = 1
		if h1440 == -1:
			headerFontHeight: int = headerFontMetrics.height()
			childFontHeight: int = childFontMetrics.height()
			headerTotalHeight: int = int(math.ceil(headerFontHeight * (1 + lineSpacingFactor)))
			childTotalHeight: int = int(math.ceil(childFontHeight * (1 + lineSpacingFactor)))
			allChildrenHeight: int = childTotalHeight * maxChildren
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
			wReal = resizeYFrom1440p(h1440)

		self.widgetRoot.move(x1440, y1440)
		self.widgetRoot.setFixedSize(wReal, hReal)


class Overlay():
	def __init__(self):
		global overlay
		overlay = self
		
		self.displayW, self.displayH = pyautogui.size()
		self.displayH_half = int(self.displayH / 2)
		
		app = QtWidgets.QApplication(list[str]())
		window = QtWidgets.QMainWindow()
		self.window = window
		window.setAttribute(QtCore.Qt.WA_TranslucentBackground)
		window.setWindowFlags(QtCore.Qt.FramelessWindowHint)
		window.setFixedSize(self.displayW, self.displayH)

		#self.createLabel("First Label", 900, 200)
		#self.createLabel("Second label", 0, 0, alignment= Qt.AlignTop | Qt.AlignRight)
		LeaderboardWidget(0, 870, "Name Leaderboard", self.createLabel, self.window, h1440=1440-870, alignment= Qt.AlignLeft | Qt.AlignTop)

		window.show()
		app.exec()
	
	def createLabel(self, text: str, x1440: int = -1, y1440: int = -1, font: str = "Lucidia Console", fontSize: int = 80, parent = None, outline = QColorConstants.White, fill = QColorConstants.Black, outlineThickness: float = 1/20, alignment: Qt.Alignment | Qt.AlignmentFlag = Qt.AlignTop | Qt.AlignLeft) -> OutlinedLabel:
		realX, realY = resizePointArrFrom1440p(x1440, y1440)
		styleSheet: str = f"font-family: {font}; font-size: {fontSize}pt; font-weight: bold;"
		
		#if parent is None:
		#	parent = self.window
		parent = self.window

		label: OutlinedLabel = OutlinedLabel(text, parent = parent)
		label.setStyleSheet(styleSheet)
		label.setPen(outline)
		label.setBrush(fill)
		label.setOutlineThickness(outlineThickness)
		label.setFixedSize(self.displayW, self.displayH)
		label.setAlignment(alignment)
		if x1440 != -1 and y1440 != -1:
			label.move(realX, realY)
		return label
		
		


overlay: Overlay
def getOverlay() -> Overlay:
	return overlay


Overlay()