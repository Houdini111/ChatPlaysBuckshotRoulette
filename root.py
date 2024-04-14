from threading import Thread
import logging
from time import sleep

from scripts.overlay import Overlay, getOverlay
from scripts.bathroom import throughToGameRoom
from scripts.waiver import waive
from scripts.gameRunner import GameRunner
from scripts.log import log
from bot.chatbot import Chatbot, getChatbot

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding="UTF-8", 
    level=logging.INFO, 
    handlers=[
        logging.FileHandler("LOG.log"),
        logging.StreamHandler()
    ]
)

def startGame() -> None:
	chatOverlay: Overlay = Overlay()
	bot: Chatbot = getChatbot()
	gameThread = Thread(target = runGame)
	botThread = Thread(target = bot.run)
	gameThread.start()
	botThread.start()
	#Required to be on main thread becauase they say so...
	chatOverlay.run()

def runGame() -> None:
	log("Starting game bot.")
	while(True):
		throughToGameRoom()
		waive()
		runner = GameRunner()
		runner.go()
		#If it gets back here then it means the player died, so go through the whole process again. 

if __name__ == '__main__':
	startGame()