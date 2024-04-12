from threading import Thread

from scripts.bathroom import throughToGameRoom
from scripts.waiver import waive
from scripts.gameRunner import GameRunner
from scripts.log import log
from scripts.overlay import Overlay

def startGame(name: str) -> None:
	chatOverlay: Overlay = Overlay()
	thread = Thread(target = runGame, args = [name,chatOverlay ])
	thread.start()
	chatOverlay.run()

def runGame(name: str, chatOverlay: Overlay) -> None:
	log("Starting game bot.")
	while(True):
		throughToGameRoom()
		waive(name)
		runner = GameRunner(chatOverlay)
		runner.go()
		#If it gets back here then it means the player died, so go through the whole process again. 

startGame('Chat')