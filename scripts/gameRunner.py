from time import sleep

from basicActions import up
from pixelPeep import Peeper, AllBlackPeep, AnyWhitePeep, OCRScoreboardPeep, RangePeep
from items import itemBoxCursorVisible, grabItems, clearItems
from playerActions import doAction
from bathroom import inStartingBathroom
from waiver import getPlayerName
from log import log

#TODO: 
#  Item place logic sometimes skipping squares
#  Sometimes activating endless goes to leaderboards instead

class GameRunner():
	def __init__(self):
		self.roundsCleared = 0
		
		#TODO: Move these definitions to their own class/file
		self.noDialogueTextBoxPeeper = Peeper("NoDialogueTextBoxPeeper", 
			RangePeep("noDialogueLeft", 10, 100, False, 577, 1153, 11, 173),
			RangePeep("noDialogueRight", 10, 100, False, 1972, 1153, 11, 173)
		)
		self.staticBoardPeeper = Peeper("StaticBoardPeeper", 
			AllBlackPeep("staticBoardBlackTop", 1159, 31, 168, 1),
			AllBlackPeep("staticBoardBlackLeft", 3, 488, 12, 12),
			AnyWhitePeep("staticBoardBulletSquare", 1477, 389, 50, 53),
			AllBlackPeep("staticBoardScoreboardBlack", 2039, 347, 7, 7),
			self.noDialogueTextBoxPeeper
		)
		self.gunCursorVisiblePeeper = Peeper("GunCursorVisiblePeeper",
			AnyWhitePeep("gunCursorTopLeft", 1170, 359, 20, 1),
			AnyWhitePeep("gunCursorBottomRight", 1306, 490, 20, 1)
		)
		self.clearingItemsPeeper = Peeper("ClearingItemsPeeper",
			AllBlackPeep("topLeftItemSectionIsBlack", 1306, 490, 30, 30),
			AllBlackPeep("topRightItemSectionIsIsBlack", 1485, 266, 25, 25),
			AllBlackPeep("bottomLeftItemSectionIsBlack", 719, 760, 25, 25),
			AllBlackPeep("bottomRightItemSectionIsBlack", 1751, 957, 25, 25),
			AnyWhitePeep("centerLineWhite", 708, 424, 10, 10),
			AnyWhitePeep("bulletSquareWhite", 1475, 392, 25, 25)
		)
		self.roundIsWonPeeper = Peeper("RoundIsWonPeeper",
			AllBlackPeep("scoreboardLeftBlack", 786, 475, 40, 150),
			AllBlackPeep("scoreboardRightBlack", 1539, 700, 40, 150),
			AnyWhitePeep("bulletSquareWhite", 675, 1246, 72, 72),
			AnyWhitePeep("dealerItemSquare8White", 303, 962, 65, 65),
			AllBlackPeep("blackAboveScoreboard", 615, 120, 31, 69),
			OCRScoreboardPeep("OCRScoreboardPlayerWins", f"{getPlayerName()} WINS")
		)
		
	def noDialogueTextBoxVisible(self) -> bool:
		return self.noDialogueTextBoxPeeper.passes()

	def staticBoard(self) -> bool:
		return self.staticBoardPeeper.passes()
	
	def gunCursorVisible(self) -> bool:
		return self.gunCursorVisiblePeeper.passes()
	
	def checkForClearingItems(self) -> bool:
		return self.clearingItemsPeeper.passes()

	def playerTurn(self) -> bool:
		log("Beginning player turn check")
		if not self.staticBoard():
			log("Failed player turn check on first static board check")
			return False
		up()
		if not self.gunCursorVisible():
			log("Failed player turn  check on first gun cursor check")
			return False
		sleep(0.1)
		#Double check to try to avoid coincidences
		if not self.staticBoard():
			log("Failed player turn check on second static board check")
			return False
		up()
		if not self.gunCursorVisible():
			log("Failed player turn  check on second gun cursor check")
			return False
		return True
	
	def checkForRoundIsWon(self) -> bool:
		if self.roundIsWonPeeper.passes():
			self.winRound()
			return True
		return False

	def winRound(self):
		self.roundsCleared += 1
		log("################")
		log(f"## Rounds cleared: {self.roundsCleared}")
		log("################")
		if self.roundsCleared == 3:
			log("################")
			log("## Double or Nothing set cleared!")
			log("################")
			self.roundsCleared = 0
			#TODO: Choose to begin a new double or nothing set

			#Do NOT clear items
		else:
			clearItems()

	def hasPlayerLost(self) -> bool:
		return inStartingBathroom()

	def go(self) -> None:
		while(True):
			log("Waiting for player turn")
			while not self.playerTurn():
				if itemBoxCursorVisible():
					log("While waiting for the player's turn the item box was found to be open. Grabbing items.")
					grabItems()
					continue
				self.checkForClearingItems()
				self.checkForRoundIsWon()
				if self.hasPlayerLost():
					log("Player found to have lost. Returning to bathroom logic.")
					return
				sleep(0.5)
			log("Should be player turn now.")
			while (True):
				request = input("Next? ")
				if doAction(request):
					break