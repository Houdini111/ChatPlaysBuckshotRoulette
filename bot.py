import pyautogui
from time import sleep
import colorsys

from bathroom import throughToGameRoom
from waiver import waive
from game import grabItems, awaitInputs
from image import scoreboardText

def startGame(name: str):
	while(True):
		throughToGameRoom()
		waive(name)
		awaitInputs()
		#If it gets back here then it means the player died, so go through the whole process again. 
	
startGame('Chat')

#sleep(2)
#print(scoreboardText())