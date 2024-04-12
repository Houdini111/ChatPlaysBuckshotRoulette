from bathroom import throughToGameRoom
from waiver import waive
from gameRunner import GameRunner

def startGame(name: str):
	while(True):
		throughToGameRoom()
		waive(name)
		runner = GameRunner()
		runner.go()
		#If it gets back here then it means the player died, so go through the whole process again. 
	
startGame('Chat')