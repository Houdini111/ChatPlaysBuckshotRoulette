import sys
import asyncio
import platform
from threading import Thread
import logging
import logging.handlers
from time import sleep

from shared.streamToLogger import StreamToLogger
from shared.config import getRunChatbot, getRunGamebot, getRunOverlay
from overlay.overlay import Overlay
from game.bathroom import throughToGameRoom
from game.waiver import waive
from game.gameRunner import GameRunner
from bot.chatbot import createAndStartChatbot, createAndStartChatbotThread


fileHandler: logging.handlers.RotatingFileHandler = logging.handlers.RotatingFileHandler("LOG.log", backupCount=3)
fileHandler.setLevel(logging.DEBUG)
consoleHandler: logging.StreamHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.INFO)
logging.basicConfig(
    format='%(asctime)s   %(levelname)-8s %(filename)15s:%(lineno)4d ->%(funcName)-30s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding="UTF-8",
	level=logging.NOTSET, #So it doesn't override the logger's levels
	handlers=[fileHandler, consoleHandler]
)

stdErrLogger = logging.getLogger("STDERR")
stdErrLoggerStream = StreamToLogger(stdErrLogger, logging.ERROR)
sys.stderr = stdErrLoggerStream

logger = logging.getLogger(__name__)

#TODO: 
#  Option for vote display stats on/off. 
#  Option for vote guides on/off
#     
#  Make dealer item circle dotted when winning vote isn't a dealer item, to show winning dealer item in case the vote swings
#  BUG: Fullscreen vote display dealer text not clearing? 
#  
#  Round number, 
#  Double or nothing set number
#  Countdown clock? for voting time. See https://stackoverflow.com/a/17985217 for circle
#  Voting stats? (absolute, percent, bars, pie chart)
#  The names and votes of chatters as they come in?
#
#  Sometimes bugs -- These might all be fixed
#    * Same player vote for same item, different dealer item is double counted? 
#         "Winning action of [USE 1 2] won with a vote count of 2 (200%)"
#    *         Maybe fixed?   Sometimes winning action vote text is wrong. Somestimes doesn't include adrenaline item number.
#    * Sometimes adrenaline item votes for the same player item don't combine.


def initAsyncio():
	if platform.system() == "Windows":
		asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

def startGame() -> None:
	logger.info("Starting all processes")
	initAsyncio()

	chatOverlay: Overlay = None
	if getRunOverlay():
		chatOverlay: Overlay = Overlay()
	else:
		logger.warning("WARNING: Config says to not run overlay! Will not run correctly!")
	
	if getRunChatbot():
		createAndStartChatbotThread()
		#createAndStartChatbot() #For running just the bot. Be sure to remove the overlay connections.
	else:
		logger.warning("WARNING: Config says to not run chatbot! Will not run correctly!")
		
	if getRunGamebot():	
		gameThread = Thread(target = runGame)
		gameThread.start()
	else:
		logger.warning("WARNING: Config says to not run gamebot! Will not run correctly!")
	
	# And similar to TwithcIO, Tkinter has its own requirement. 
	# It literally just refuses to run if it's not on the main thread.
	# At least TwitchIO tries... 
	if getRunOverlay():
		chatOverlay.run()

def runGame() -> None:
	logger.info("Starting game bot.")
	while(True):
		throughToGameRoom()
		waive()
		runner = GameRunner()
		runner.go()
		#If it gets back here then it means the player died, so go through the whole process again. 

if __name__ == '__main__':
	startGame()