from threading import Thread
import logging
import logging.handlers
from time import sleep

from overlay.overlay import Overlay, getOverlay
from game.bathroom import throughToGameRoom
from game.waiver import waive
from game.gameRunner import GameRunner
from bot.chatbot import Chatbot, getChatbot

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

logger = logging.getLogger(__name__)

#TODO: 
#  Handle adrenaline (display don't show numbers for close but show them far?)
#  End of round 
#  Fix not all messages sending (action ones)

def startGame() -> None:
	logger.info("Starting all processes")
	chatOverlay: Overlay = Overlay()
	bot: Chatbot = getChatbot()
	gameThread = Thread(target = runGame)
	botThread = Thread(target = bot.run)
	gameThread.start()
	botThread.start()
	#Required to be on main thread becauase they say so...
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