import logging
from msvcrt import getch
from time import sleep

from .items import getItemManager
from .basicActions import up, left, confirm
from .pixelPeep import Peeper, AllBlackPeep, AnyWhitePeep, AnyNotBlackPeep
from .playerActions import Action, execute
from .bathroom import inStartingBathroom
from .waiver import getPlayerName
from shared.config import getActionVotePeriod
from shared.actions import parseAction
from overlay.overlay import Overlay, getOverlay
from overlay.status import status
from bot.chatbot import getChatbot

logger = logging.getLogger(__name__)

#TODO: 
#  Item place logic sometimes skipping squares
#  Sometimes activating endless goes to leaderboards instead

class GameRunner():
	def __init__(self):
		self.roundsCleared = 0
		
		#TODO: Move these definitions to their own class/file
		self.noDialogueTextBoxPeeper = Peeper("NoDialogueTextBoxPeeper", 
			AnyNotBlackPeep("noDialogueLeft", 577, 1153, 11, 173),
			AnyNotBlackPeep("noDialogueRight", 1972, 1153, 11, 173)
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
			AllBlackPeep("scoreboardDealerNameNotVisiblePeep", 773, 493, 124, 18),
			AnyNotBlackPeep("scoreboardTextNotBlackPeep", 871, 595, 500, 100),
			AllBlackPeep("scoreboardNoRoundTextPeep", 1164, 755, 100, 15)
		)
		
		self.doubleOrNothingWinPeeper = Peeper("DoubleOrNothingPeeper",
			AllBlackPeep("aboveRadioBlack", 1615, 237, 19, 19),
			AllBlackPeep("belowScoreNumbersBlack", 1262, 1106, 20, 20),
			AllBlackPeep("leftPillarBlack", 100, 490, 11, 11),
			AnyWhitePeep("radioShineRightWhite", 1697, 317, 15, 15),
			AnyWhitePeep("radioShineLeftWhite", 1248, 349, 10, 10),
			AnyWhitePeep("centerLineWhite", 1256, 1414, 14, 14)
		)
		
		self.doubleOrNothingCursorPeeper = Peeper("DoubleOrNothingCursorPeeper",
			AnyWhitePeep("doubleOrNothingCursorPeeper", 705, 156, 32, 32)									
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
		logger.info("Beginning player turn check")
		if not self.staticBoard():
			logger.debug("Failed player turn check on first static board check")
			return False
		up()
		if not self.gunCursorVisible():
			logger.debug("Failed player turn  check on first gun cursor check")
			return False
		sleep(0.1)
		#Double check to try to avoid coincidences
		if not self.staticBoard():
			logger.debug("Failed player turn check on second static board check")
			return False
		up()
		if not self.gunCursorVisible():
			logger.debug("Failed player turn  check on second gun cursor check")
			return False
		return True
	
	def checkForRoundIsWon(self) -> bool:
		if (self.roundIsWonPeeper.passes()) or \
			(self.roundsCleared == 2 and self.doubleOrNothingWinPeeper.passes()):
			self.winRound()
			return True
		return False

	def winRound(self):
		self.roundsCleared += 1
		logger.info("################")
		logger.info(f"## Rounds cleared: {self.roundsCleared}")
		logger.info("################")
		if self.roundsCleared == 3:
			logger.info("################")
			logger.info("## Double or Nothing set cleared!")
			logger.info("################")
			self.roundsCleared = 0
			#TODO: Choose to begin a new double or nothing set
			status("Waiting to see cursor for double or nothing")
			while not self.doubleOrNothingCursorPeeper.passes():
				sleep(0.2)
				left()
			status("Confirming to start a new double or nothing set")
			confirm()
			#Do NOT clear items. The game keeps them for whatever reason.
		else:
			getItemManager().clearItems()
		sleep(4) #Wait for extra to make sure round wins don't get counted multiple times

	def hasPlayerLost(self) -> bool:
		if not inStartingBathroom():
			return False
		sleep(0.1)
		return inStartingBathroom()

	def go(self) -> None:
		while(True):
			status("Waiting for player turn")
			while not self.playerTurn():
				if getItemManager().itemBoxCursorVisible():
					logger.info("While waiting for the player's turn the item box was found to be open. Grabbing items.")
					getItemManager().grabItemsV2()
					continue
				self.checkForClearingItems()
				self.checkForRoundIsWon()
				if self.hasPlayerLost():
					logger.info("Player found to have lost. Returning to bathroom logic.")
					getItemManager().clearItems()
					return
				sleep(0.5)
			logger.info("Should be player turn now. Refreshing player items.")
			getItemManager().refreshPlayerItems()
			status("Awaiting player input")
			getOverlay().displayItemActionGuides(getItemManager().getAllCurrentItemPositions())
			actionSuccess: bool = False
			retry: bool = False
			invalid: bool = False
			getChatbot().clearActionVotes()
			logger.info("Starting input loop")
			while not actionSuccess:
				if not invalid:
					logger.debug("Not invalid user input (which would be a retry), opening chat voting")
					getChatbot().openActionInputVoting(retry)
					logger.debug(f"Action voting opened. Waiting for input for {getActionVotePeriod()}")
					sleep(getActionVotePeriod())
					logger.debug("Waiting for input over. Closing action voting")
					getChatbot().closeActionInputVoting(retry)
					logger.debug("Action voting closed")
				while (True):
					#request = input("Next? ")
					action: Action | None = getChatbot().getVotedAction()
					if action is None: #Tie or something. Re-open votes
						retry = True
						invalid = False
						break
					if action.valid():
						getOverlay().clearActionOverlay()
						execute(action)
						actionSuccess = True
						break
					#Invalid action chosen, check next
					getChatbot().sendMessage(f"Top voted action \"{action}\" was invalid. Attempting next winner.")
					retry = False
					invalid = True
					getChatbot().removeVotedAction(action)
				