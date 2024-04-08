import pyautogui
from time import sleep

from bathroom import throughToGameRoom
from waiver import waive
from game import grabItems, awaitInputs

def startGame(name: str):
	throughToGameRoom()
	waive(name)
	grabItems()
	awaitInputs()
	

startGame('Houdini')