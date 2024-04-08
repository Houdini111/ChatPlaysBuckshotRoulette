from time import sleep
import colorsys
from focus import waitFocused
from screenColors import getPixelAreaBy1440p
from basicActions import confirm, left, right, up, down, enterDirections, anyUse

def throughToGameRoom():
	enableEndless()
	exitBathroom()
	enterGameRoom()

def moveCursorToBathroomDoor():
	print("### Moving cursor to bathroom door")
	waitFocused()
	up() #Make cursor show without changing selection
	for movements in range(10): #Tries before movement
		#Give each section 5 tries, in case the check missed
		for i in range(5): 
			#Targeting bottom left of cursor. This should be a large enough area to see it, even with the swaying.
			areaColors = getPixelAreaBy1440p(1432, 712, 40, 1)
			for axisOne in areaColors: #Don't know if it's columns or rows but it doesn't matter
				for pixel in axisOne:
					(h, s, v) = colorsys.rgb_to_hsv(pixel[0], pixel[1], pixel[2])
					if v >= 50:
						print(f"Cursor should be on door now. Detected Value of {v}. RGB: {pixel}")
						return
			sleep(0.1)
		print("Didn't find cursor on door. Moving cursor and trying again.")
		right()
	raise Exception("Couldn't locate door cursor")

def enableEndless():
	print("##### Enabling endless")
	moveCursorToBathroomDoor()
	left()
	sleep(1)
	confirm()
	print("Waiting for pills menu to open fully")
	sleep(2)
	left()
	confirm()
	print("Pills consumed. Waiting for reload to bathroom.")
	sleep(5)

def exitBathroom():
	print("##### Exiting bathroom")
	anyUse()
	sleep(6) #Do I need more? Can I get away with less?
	
def enterGameRoom():
	print("##### Entering game room")
	anyUse()
	sleep(10) #Do I need more? Can I get away with less?