import bathroom
import waiver
import gameRunner

def startGame(name: str):
	while(True):
		bathroom.throughToGameRoom()
		waiver.waive(name)
		gameRunner = gameRunner.GameRunner()
		gameRunner.go()
		#If it gets back here then it means the player died, so go through the whole process again. 
	
startGame('Chat')