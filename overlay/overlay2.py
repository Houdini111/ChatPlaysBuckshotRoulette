import sys
import pyautogui
import logging
import math
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QColorConstants
from PyQt5.QtCore import Qt

from .overlay import Overlay, setOverlayToThis
from .OutlinedLabel import OutlinedLabel
from .leaderboard2 import LeaderboardWidget
from .nameLeaderboard2 import NameLeaderboard
from shared.util import resizePointArrFrom1440p
from bot.vote import VotingTallyEntry

logger = logging.getLogger(__name__)

class Overlay2(Overlay):
	def __init__(self):
		setOverlayToThis(self)
		
		self.displayW, self.displayH = pyautogui.size()
		self.displayH_half = int(self.displayH / 2)
		
		self.app = QtWidgets.QApplication(list[str]())
		window = QtWidgets.QMainWindow()
		self.window = window
		window.setAttribute(QtCore.Qt.WA_TranslucentBackground)
		window.setWindowFlags(QtCore.Qt.FramelessWindowHint)
		window.setFixedSize(self.displayW, self.displayH)

		self.baseFontSize: int = (math.ceil(80 * (float(self.displayH) / 1440))) #80 is the size I want at 1440p

		leaderboardWidget: LeaderboardWidget = LeaderboardWidget(0, 870, "Name Leaderboard", self.createLabel, self.window, h1440=1440-870, alignment= Qt.AlignLeft | Qt.AlignTop)
		self.nameLeaderboard = NameLeaderboard(leaderboardWidget)

		statusTextFontSize = int(self.baseFontSize*50/80)
		self.statusText = self.createLabel("Here is a sample status text. Let's see if it works just fine the first time.", 5, 0, fontSize= statusTextFontSize)

	def start(self):
		self.window.show()
		self.app.exec()
	
	def stop(self):
		self.app.quit()

	def createLabel(self, text: str, x1440: int = -1, y1440: int = -1, fontName: str = "Lucida Console", fontSize: int = 80, parent = None, outline = QColorConstants.White, fill = QColorConstants.Black, outlineThickness: float = 1/20, alignment: Qt.Alignment | Qt.AlignmentFlag = Qt.AlignTop | Qt.AlignLeft) -> OutlinedLabel:
		realX, realY = resizePointArrFrom1440p(x1440, y1440)
		font = QtGui.QFont(fontName, fontSize, QtGui.QFont.Weight.Bold)
		font.setStyleHint(QtGui.QFont.StyleHint.Monospace)
		font.setFamily(fontName)
		
		#if parent is None:
		#	parent = self.window
		parent = self.window

		label: OutlinedLabel = OutlinedLabel(text, parent = parent)
		label.setFont(font)
		label.setPen(outline)
		label.setBrush(fill)
		label.setOutlineThickness(outlineThickness)
		label.setFixedSize(self.displayW, self.displayH)
		label.setAlignment(alignment)
		if x1440 != -1 and y1440 != -1:
			label.move(realX, realY)
		logger.info(f"FONT: {QtGui.QFontInfo(label.font()).family()}")
		return label
	
	def updateStatusText(self, text: str) -> None:
		self.statusText.setText(text)
		
	def clearOldNameLeaderboard(self) -> None:
		logger.info("Clearing old name leaderboard")
		self.nameLeaderboard.clearRows()

	def drawNameVoteLeaderboard(self, votes: list[VotingTallyEntry]) -> None:
		self.nameLeaderboard.displayVotes(votes)
		
	def displayItemActionGuides(self, numbersToDraw: list[int]) -> None:
		pass
		
	def drawActionVotes(self, actionVotes: list[VotingTallyEntry], adrenalineItemVotes: list[VotingTallyEntry]) -> None:
		pass
		
	def clearActionOverlay(self) -> None:
		pass
		
	def clearActionVoteStatic(self) -> None:
		pass
		
	def clearActionVotes(self) -> None:
		pass
		
	def hideActionReticle(self) -> None:
		pass
	
	def startCountdown(self) -> None:
		pass

	def hideCountdown(self) -> None:
		pass