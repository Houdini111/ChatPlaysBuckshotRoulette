import sys
import asyncio
import platform
from threading import Thread
import logging
import logging.handlers
from time import sleep

from shared.streamToLogger import StreamToLogger
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
    format='%(asctime)s   %(levelname)-8s %(filename)15s->%(funcName)-30s %(message)s',
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
#  Handle adrenaline
#      - Combine votes for adrenaline items (by checking if they have multiple parameters)
#      - Display votes for dealer items? Or just say which one won afterwards?

def initAsyncio():
	if platform.system() == "Windows":
		asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

def startGame() -> None:
	logger.info("Starting all processes")
	initAsyncio()

	chatOverlay: Overlay = Overlay()
	
	createAndStartChatbotThread()
	#createAndStartChatbot() #For running just the bot. Be sure to remove the overlay connections.
	
	gameThread = Thread(target = runGame)
	gameThread.start()
	
	# And similar to TwithcIO, Tkinter has its own requirement. 
	# It literally just refuses to run if it's not on the main thread.
	# At least TwitchIO tries... 
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