from ctypes import alignment
import sys
from turtle import position
import pyautogui
import logging
import math
import inspect
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QColorConstants
from PyQt5.QtCore import Qt

from .overlay import Overlay, setOverlayToThis
from .OutlinedLabel import OutlinedLabel
from .leaderboard2 import LeaderboardWidget, Leaderboard
from .nameLeaderboard2 import NameLeaderboard
from .actionVoteDisplay2 import ActionVoteDisplay
from .sidebarVoteDisplay2 import SidebarVoteDisplay, ActionLeaderboard, AdrenalineLeaderboard
from shared.util import resizePointArrFrom1440p
from shared.config import useSidebarActionOverlay
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
		layout = QtWidgets.QGridLayout()
		window.setLayout(layout)
		self.layout = layout
		window.setAttribute(QtCore.Qt.WA_TranslucentBackground)
		window.setWindowFlags(QtCore.Qt.FramelessWindowHint)
		window.setFixedSize(self.displayW, self.displayH)

		self.baseFontSize: int = (math.ceil(80 * (float(self.displayH) / 1440))) #80 is the size I want at 1440p


		#statusWidget: QtWidgets.QFrame = QtWidgets.QFrame(parent= self.window)
		#statusLayout = QtWidgets.QVBoxLayout()
		#statusWidget.setLayout(statusLayout)
		#statusWidget = self.window
		#statusWidget.setParent(self.window)
		#statusWidget.setFixedSize(self.displayW, self.displayH)


		statusTextFontSize = int(self.baseFontSize*50/80)
		#self.statusText = self.createLabel("Here is a sample status text. Let's see if it works just fine the first time.", 5, 0, fontSize= statusTextFontSize, parent = statusWidget)#, w1440= 2560, h1440= 1440)
		self.statusText = QtWidgets.QLabel("Here is a sample status text. Let's see if it works just fine the first time.", parent=self.window)
		font = QtGui.QFont("Lucida Console", statusTextFontSize, QtGui.QFont.Weight.Bold)
		font.setStyleHint(QtGui.QFont.StyleHint.Monospace)
		font.setFamily("Lucida Console")
		self.statusText.setFont(font)
		self.layout.addWidget(self.statusText)
		self.statusText.setLineWidth(5)
		self.statusText.setMidLineWidth(5)
		self.statusText.setFrameStyle(QtWidgets.QFrame.Shape.Box)
		self.statusText.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
		self.statusText.setSizePolicy(QtWidgets.QSizePolicy.Policy.Ignored, QtWidgets.QSizePolicy.Policy.Ignored)
		#statusLayout.addWidget(self.statusText)
		
		##############
		#TODO: FIGURE OUT WHY THIS DOESN'T GET BIGGER NO MATTER WHAT I DO
		##############

		nameLeaderboardWidget: LeaderboardWidget = LeaderboardWidget(0, 870, "Name Leaderboard", self.createLabel, parent= self.window, h1440=1440-870, alignment= Qt.AlignLeft | Qt.AlignTop)
		self.nameLeaderboard = NameLeaderboard(nameLeaderboardWidget)
		layout.addWidget(nameLeaderboardWidget.widgetRoot)
		
		self.actionOverlay: ActionVoteDisplay
		if useSidebarActionOverlay():
			actionLeaderboardWidget: LeaderboardWidget = LeaderboardWidget(2560, 0, "Action Votes", self.createLabel, parent= self.window, h1440=int(1440/2), alignment= (Qt.AlignmentFlag)(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight), largestExpectedText= ActionLeaderboard.sampleLargestText())
			actionLeaderboard: ActionLeaderboard = ActionLeaderboard(actionLeaderboardWidget)
			layout.addWidget(actionLeaderboardWidget.widgetRoot)
			adrenalineLeaderboardWidget: LeaderboardWidget = LeaderboardWidget(2560, int(1440/2), "Adrenaline Votes", self.createLabel, parent= self.window, h1440=int(1440/2), alignment= (Qt.AlignmentFlag)(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight), largestExpectedText= AdrenalineLeaderboard.sampleLargestText())
			adrenalineLeaderboard: AdrenalineLeaderboard = AdrenalineLeaderboard(adrenalineLeaderboardWidget)
			layout.addWidget(adrenalineLeaderboardWidget.widgetRoot)
			self.actionOverlay = SidebarVoteDisplay(actionLeaderboard, adrenalineLeaderboard)
		else:
			#TODO: 
			#self.actionOverlay = FullScreenVoteDisplay()
			pass
		
		logger.debug(f"Status text Position: ({self.statusText.x()}, {self.statusText.y()}) Size: ({self.statusText.width()}, {self.statusText.height()})")

		
	def start(self):
		self.window.show()
		self.app.exec()
	
	def stop(self):
		self.app.quit()

	def createLabel(self, text: str, x1440: int = -1, y1440: int = -1, fontName: str = "Lucida Console", fontSize: int = 80, parent = None, outline = QColorConstants.White, fill = QColorConstants.Black, outlineThickness: float = 1/20, alignment: Qt.Alignment | Qt.AlignmentFlag = Qt.AlignTop | Qt.AlignLeft, w1440: int = -1, h1440: int = -1) -> OutlinedLabel:
		realX, realY = resizePointArrFrom1440p(x1440, y1440)
		realW, realH = resizePointArrFrom1440p(w1440, h1440)
		font = QtGui.QFont(fontName, fontSize, QtGui.QFont.Weight.Bold)
		font.setStyleHint(QtGui.QFont.StyleHint.Monospace)
		font.setFamily(fontName)
		
		#if parent is None:
		#	parent = self.window
		
		#parent = self.window
		#parent = self.layout
		#parent = parent

		#label: QtWidgets.QLabel = QtWidgets.QLabel(text, parent= parent)
		#label.setFont(font)
		#label.setPen(outline)
		label: OutlinedLabel = OutlinedLabel(text, parent = parent)
		label.setFont(font)
		label.setPen(outline)
		label.setBrush(fill)
		label.setOutlineThickness(outlineThickness)
		posBefore = label.pos()
		positionText = ""
		#label.setFixedSize(self.displayW, self.displayH)
		label.setAlignment(alignment)
		if x1440 != -1 and y1440 != -1:
			if x1440 == -1:
				realX = label.pos().x()
			if y1440 == -1:
				realY = label.pos().y()
			positionText = f"Using overridden position of ({realX}, {realY})"
			label.move(realX, realY)
		else:
			positionText = f"Using default position of ({posBefore.x()}, {posBefore.y()})"
		sizeBefore = label.size()
		sizeText = ""
		if w1440 != -1 and h1440 != -1:
			if w1440 == -1:
				realW = label.width()
			if h1440 == -1:
				realH = label.height()
			sizeText = f"Using overridden size of ({realW}, {realH})"
			#label.setSizePolicy(QtWidgets.QSizePolicy.Policy.Ignored, QtWidgets.QSizePolicy.Policy.Ignored)
			#label.setMinimumSize(realW, realH)
		else:
			sizeText = f"Using default size of ({sizeBefore.width()}, {sizeBefore.height()})"
		
		#label.setSizePolicy(QtWidgets.QSizePolicy.Policy.Ignored, QtWidgets.QSizePolicy.Policy.Ignored)
		
		logger.info(f"Creating label with text\"{text}\". {sizeText}. {positionText}")
		logger.info(f"FONT: {QtGui.QFontInfo(label.font()).family()}")
		
		#TODO: Make config to show
		label.setLineWidth(5)
		label.setMidLineWidth(5)
		label.setFrameStyle(QtWidgets.QFrame.Shape.Box)
		label.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
		
		return label
	
	def updateStatusText(self, text: str) -> None:
		logger.info(f"Updating status to \"{text}\"")
		#self.statusText.setText(text)
		
	def clearOldNameLeaderboard(self) -> None:
		logger.info("Clearing old name leaderboard")
		self.nameLeaderboard.clearRows()

	def drawNameVoteLeaderboard(self, votes: list[VotingTallyEntry]) -> None:
		logger.info(f"Overlay2 drawing {len(votes)} names to the leaderboard")
		self.nameLeaderboard.displayVotes(votes)
		
	def displayStaticActionOverlayDisplayElements(self, numbersToDraw: list[int]) -> None:
		logger.info("Overlay2 displaying static elements")
		self.actionOverlay.displayStaticElements(numbersToDraw)
		
	def drawActionVotes(self, actionVotes: list[VotingTallyEntry], adrenalineItemVotes: list[VotingTallyEntry]) -> None:
		logger.info(f"Overlay2 displaying {len(actionVotes)} action votes and {len(adrenalineItemVotes)} adrenalineVotes")
		self.actionOverlay.drawActionVotes(actionVotes, adrenalineItemVotes)
		
	def clearActionOverlay(self) -> None:
		frame: inspect.FrameInfo = inspect.stack()[1]
		file = frame.filename.split("\\ChatPlaysBuckshotRoulette\\")[1]
		funcName = frame.function
		line = frame.lineno
		logger.info(f"Overlay2 clearing action overlay, called by {file} -> {funcName} (Line: {line})")
		self.clearActionVotes()
		self.clearStaticActionVoteDisplayElements()
		self.hideActionReticle()
	
	def clearActionVotes(self) -> None:
		logger.info("Overlay2 clearing action votes")
		self.actionOverlay.clearActionVotes()

	def clearStaticActionVoteDisplayElements(self) -> None:
		logger.info("Overlay2 clearing static elements")
		self.actionOverlay.clearStaticElements()
		
	def hideActionReticle(self) -> None:
		logger.info("Overlay2 hiding action reticle")
		#TODO:
		pass