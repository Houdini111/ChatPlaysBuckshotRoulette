import math
import pyautogui
import getpixelcolor

def resizeRectFrom1440p(x1440: int, y1440: int, w1440: int, h1440: int):
	xPercent = x1440/2560
	yPercent = y1440/1440
	wPercent = w1440/2560
	hPercent = h1440/1440
	displayW, displayH = pyautogui.size()
	realX = int(math.ceil(xPercent * displayW))
	realY = int(math.ceil(yPercent * displayH))
	realW = int(math.ceil(wPercent * displayW))
	realH = int(math.ceil(hPercent * displayH))
	return [realX, realY, realW, realH]

def getPixelAreaBy1440p(x1440: int, y1440: int, w1440: int, h1440: int):
	realX, realY, realW, realH = resizeRectFrom1440p(x1440, y1440, w1440, h1440)
	return getpixelcolor.area(realX, realY, realW, realH)

def getPixelAreaAverageBy1440p(x1440: int, y1440: int, w1440: int, h1440: int):
	realX, realY, realW, realH = resizeRectFrom1440p(x1440, y1440, w1440, h1440)
	return getpixelcolor.average(realX, realY, realW, realH)