import pyautogui
from time import sleep
import colorsys

from bathroom import throughToGameRoom
from waiver import waive
from game import grabItems, awaitInputs
from image import scoreboardText

def startGame(name: str):
	throughToGameRoom()
	waive(name)
	grabItems()
	awaitInputs()
	
startGame('Chat')

#sleep(2)
#print(scoreboardText())