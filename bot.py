from scripts.bathroom import throughToGameRoom
from scripts.waiver import waive
from scripts.gameRunner import GameRunner
from scripts.log import log

def startGame(name: str) -> None:
	log("Starting game bot.")
	while(True):
		throughToGameRoom()
		waive(name)
		runner = GameRunner()
		runner.go()
		#If it gets back here then it means the player died, so go through the whole process again. 
	
startGame('Chat')