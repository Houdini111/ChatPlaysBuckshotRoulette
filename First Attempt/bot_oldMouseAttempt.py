import pyautogui
from typing import Final 
from time import sleep
import math
from classes import Action, ItemPos, Point, Resolution


class Zone():
	def __init__(self, left: float, right: float, top: float, bottom: float):
		self.left = left
		self.right = right
		self.top = top
		self.bottom = bottom
	
	def center(self, res: Resolution) -> Point:
		xPercent = (self.left + self.right)/2
		yPercent = (self.top + self.bottom)/2
		xAbs = math.floor(xPercent * res.width)
		yAbs = math.floor(yPercent * res.height)
		return Point(xAbs, yAbs, True)

#Size and position based on 16:9
GUN_POSITION_ZONE = Zone(0.42, 0.47, 0.47, 0.55) #1078 - 1208 on 2560  and  662 - 791  on 1440
SELF_POSITION_ZONE = Zone(0.47, 0.529, 0.27, 0.1368) #1208 - 1353 on 2560  and  197 to 389 on 1440
DEALER_POSITION_ZONE = Zone(0.439, 0.555, 0.844, 0.7486) #1125 - 1422 on 2560  and  1215 - 1078 on 1440
ITEM_ZONE_1 = Zone(0.245, 0.273, 0.621, 0.428) #628 - 698 on 2560  and  894 - 616 on 1440
ITEM_ZONE_2 = Zone(0.339, 0.366, 0.615, 0.433) #867 - 936 on 2560  and  885 - 624 on 1440
ITEM_ZONE_3 = Zone(0.641, 0.666, 0.615, 0.431) #1640 - 1706 on 2560  and  886 - 620 on 1440
ITEM_ZONE_4 = Zone(0.737, 0.76, 0.598, 0.443) #1887 - 1946 on 2560  and  861 - 638 on 1440
ITEM_ZONE_5 = Zone(0.154, 0.187, 0.356, 0.701) #395 - 478 on 2560  and  513 - 1010 on 1440
ITEM_ZONE_6 = Zone(0.293, 0.32, 0.388, 0.662) #749 - 820 on 2560  and  558 - 953 on 1440
ITEM_ZONE_7 = Zone(0.679, 0.715, 0.366, 0.698) #1739 - 1831 on 2560  and  527 - 1005 on 1440
ITEM_ZONE_8 = Zone(0.825, 0.852, 0.383, 0.665) #2112 - 2181 on 2560  and  551 - 958 on 1440
ITEM_ZONES = [ITEM_ZONE_1, ITEM_ZONE_2, ITEM_ZONE_3, ITEM_ZONE_4, ITEM_ZONE_5, ITEM_ZONE_6, ITEM_ZONE_7, ITEM_ZONE_8 ]


primaryResolution=None
def getResolution() -> Resolution:
	if primaryResolution is None:
		w, h = pyautogui.size()
		resolution = Resolution(h, w)
	return resolution

def clickGun():
	click(GUN_POSITION_ZONE.center(getResolution()))

def click(point: Point):
	#Library uses top left origin. Ensure proper origin
	if point.originIsTopLeft:
		point = point.bottomLeftOrigin(getResolution())
	x = point.x
	y = point.y
	print(f"Moving to [{x}, {y}]")
	pyautogui.moveTo(x, y)
	sleep(1)
	print(f"Clicking on [{x}, {y}]")
	pyautogui.click(x, y)

def chooseSelf():
	click(SELF_POSITION_ZONE.center(getResolution()))

def chooseDealer():
	click(DEALER_POSITION_ZONE.center(getResolution()))

def shootSelf():
	clickGun()
	chooseSelf()
	
def shootDealer():
	clickGun()
	chooseDealer()
	
def useItem(num):
	zone = ITEM_ZONES[num-1]
	click(zone.center(getResolution()))
	
	
	

sleep(2) #1 second
#clickGun()
#pyautogui.moveTo(100, 100)
#shootDealer()
useItem(8)