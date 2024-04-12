from time import sleep

import basicActions
import items
import pixelPeep
import playerActions
import screenColors
import waiver
import image
import bathroom


#TODO: 
#  Item place logic sometimes skipping squares
#  Sometimes activating endless goes to leaderboards instead

class GameRunner():
	def __init__(self):
		self.roundsCleared = 0
		
		self.noDialogueTextBoxPeeper = pixelPeep.Peeper("NoDialogueTextBoxPeeper", 
			pixelPeep.WhitePeep("noDialogueLeft", 577, 1153, 11, 173),
			pixelPeep.WhitePeep("noDialogueRight", 1972, 1972, 11, 173)
		)
		self.staticBoardPeeper = pixelPeep.Peeper("StaticBoardPeeper", 
			pixelPeep.BlackPeep("staticBoardblackTop", 1159, 31, 168, 1),
			pixelPeep.BlackPeep("staticBoardblackLeft", 3, 488, 12, 12),
			pixelPeep.WhitePeep("staticBoardbulletSquare", 1477, 389, 50, 53),
			pixelPeep.WhitePeep("staticBoardscoreboardBlack", 2040, 347, 5, 5),
			self.noDialogueTextBoxPeeper,
		)
		self.gunCursorVisiblePeeper = pixelPeep.Peeper("GunCursorVisiblePeeper",
			pixelPeep.WhitePeep("gunCursorTopLeft", 1170, 359, 20, 1),
			pixelPeep.WhitePeep("gunCursorBottomRight", 1306, 490, 20, 1)
		)
		self.clearingItemsPeeper = pixelPeep.Peeper("ClearingItemsPeeper",
			pixelPeep.BlackPeep("topLeftItemSectionIsBlack", 1306, 490, 30, 30),
			pixelPeep.BlackPeep("topRightItemSectionIsIsBlack", 1485, 266, 25, 25),
			pixelPeep.BlackPeep("bottomLeftItemSectionIsBlack", 719, 760, 25, 25),
			pixelPeep.BlackPeep("bottomRightItemSectionIsBlack", 1751, 957, 25, 25),
			pixelPeep.WhitePeep("centerLineWhite", 708, 424, 10, 10),
			pixelPeep.WhitePeep("bulletSquareWhite", 1751, 1473, 15, 15)
		)
		self.roundIsWonPeeper = pixelPeep.Peeper("RoundIsWonPeeper",
			pixelPeep.BlackPeep("scoreboardLeftBlack", 786, 418, 40, 150),
			pixelPeep.BlackPeep("scoreboardRightBlack", 1493, 646, 99, 249),
			pixelPeep.WhitePeep("bulletSquareWhite", 675, 1246, 72, 72),
			pixelPeep.WhitePeep("dealerItemSquare8White", 303, 962, 65, 65),
			pixelPeep.WhitePeep("blackAboveScoreboard", 615, 120, 31, 69),
			pixelPeep.OCRScoreboardPeep("OCRScoreboardPlayerWins", f"{getPlayerName()} WINS")
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
		print("### Beginning player turn check")
		if not self.staticBoard():
			print("Failed player turn check on first static board check")
			return False
		basicActions.up()
		if not self.gunCursorVisible():
			print("Failed player turn  check on first gun cursor check")
			return False
		sleep(0.1)
		#Double check to try to avoid coincidences
		if not self.staticBoard():
			print("Failed player turn check on second static board check")
			return False
		basicActions.up()
		if not self.gunCursorVisible():
			print("Failed player turn  check on second gun cursor check")
			return False
		return True
	
	def checkForRoundIsWon(self) -> bool:
		if self.roundIsWonPeeper.passes():
			self.winRound()
			return True
		return False

	def winRound(self):
		self.roundsCleared += 1
		print("################")
		print(f"## Rounds cleared: {roundsCleared}")
		print("################")
		if roundsCleared == 3:
			print("################")
			print("## Double or Nothing set cleared!")
			print("################")
			roundsCleared = 0
			#TODO: Choose to begin a new double or nothing set

			#Do NOT clear items
		else:
			items.clearItems()

	def hasPlayerLost(self) -> bool:
		return bathroom.inStartingBathroom()

	def go(self):
		while(True):
			print("# Waiting for player turn")
			while not self.playerTurn():
				if items.itemBoxCursorVisible():
					print("# While waiting for the player's turn the item box was found to be open. Grabbing items.")
					items.grabItems(self.itemBoxIsOpen)
					continue
				self.checkForClearingItems()
				self.checkForRoundIsWon()
				if self.hasPlayerLost():
					print("#### Player found to have lost. Returning to bathroom logic.")
					return
				sleep(0.5)
			print("# Should be player turn now.")
			while (True):
				request = input("Next? ")
				if playerActions.doAction(request):
					break