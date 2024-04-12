import math
import pyautogui
import getpixelcolor
import colorsys
from deprecation import deprecated

from util import Rectangle

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

#For a 2d array of pixels
def pixelsMatch(expectedPixels, realPixels):
	if len(expectedPixels) != len(realPixels):
		print(f"Pixels don't match because first order array size is wrong. Expected: {len(expectedPixels)} Actual: {len(realPixels)}")
		return False
	for expectedAxis, realAxis in zip(expectedPixels, realPixels):
		if len(expectedAxis) != len(realAxis):
			print(f"Pixels don't match because second order array size is wrong. Expected: {len(expectedAxis)} Actual: {len(realAxis)}")
			return False
		for expectedPixel, realPixel in zip(expectedAxis, realAxis):
			if not pixelMatches(expectedPixel, realPixel):
				#print(f"Failed because pixel doesn't match. Expected {expectedPixel} Actual: {realPixel}")
				return False
	return True 

#For a single pixel
def pixelMatches(expectedPixel, realPixel) -> bool:
	return expectedPixel[0] == realPixel[0] and expectedPixel[1] == realPixel[1] and expectedPixel[2] == realPixel[2]


@deprecated(details="Use valuesInRangeInRect")
def valueUnderAmountInRect(valuePercent: float, rect: Rectangle) -> bool:
	return valueUnderAmountInArea(valuePercent, rect.x, rect.y, rect.w, rect.h)

@deprecated(details="Use valuesInRangeInArea")
def valueUnderAmountInArea(valuePercent: float, x1440: int, y1440: int, w1440: int, h1440: int) -> bool:
	return not valueOverAmountInArea(valuePercent, x1440, y1440, w1440, h1440)

@deprecated(details="Use valuesInRangeInRect")
def valueOverAmountInRect(valuePercent: float, rect: Rectangle) -> bool:
	return valueOverAmountInArea(valuePercent, rect.x, rect.y, rect.w, rect.h)

@deprecated(details="Use valuesInRangeInArea")
def valueOverAmountInArea(valuePercent: float, x1440: int, y1440: int, w1440: int, h1440: int) -> bool:
	areaColors = getPixelAreaBy1440p(x1440, y1440, w1440, h1440)
	max = 0
	valueAbsolute = float(255 * valuePercent) / 100
	for axisOne in areaColors: #Don't know if it's columns or rows but it doesn't matter
		for pixel in axisOne:
			(h, s, v) = colorsys.rgb_to_hsv(pixel[0], pixel[1], pixel[2])
			if v > max:
				max = v
			if v >= valueAbsolute:
				print(f"Found value of {v}, which is greater than the minimum {valuePercent}% (absolute: {valueAbsolute}). RGB: {pixel}")
				return True
	print(f"Did not find Value over {valuePercent}% (absolute: {valueAbsolute}). Max found: {max}")
	return False

def valuesInRangeInRect(lowPercent: float, highPercent: float, anyMode: bool, rect: Rectangle) -> bool:
	return valuesInRangeInArea(lowPercent, highPercent, anyMode, rect.x, rect.y, rect.w, rect.h)

def valuesInRangeInArea(lowPercent: float, highPercent: float, anyMode: bool, x1440: int, y1440: int, w1440: int, h1440: int) -> bool:
	areaColors = getPixelAreaBy1440p(x1440, y1440, w1440, h1440)
	maxFound = 0
	minFound = 255
	lowAbsolute = float(255 * lowPercent) / 100
	highAbsolute = float(255 * highPercent) / 100
	for axisOne in areaColors: #Don't know if it's columns or rows but it doesn't matter
		for pixel in axisOne:
			(h, s, v) = colorsys.rgb_to_hsv(pixel[0], pixel[1], pixel[2])
			if v > maxFound:
				maxFound = v
			elif v < minFound:
				minFound = v
			
			#TODO: Rather than a "mode" with checkers in here, try a resolver that you just pass the current value and the goal range
			if anyMode: 
				if v >= lowAbsolute and v <= highAbsolute:
					print(f"Found Value {v} in absolute range [{lowAbsolute}, {highPercent}] (percent range [{lowPercent}%, {highPercent}%]) during ANY mode. RGB: {pixel}. Returning True.")
					return True
			else: #ALL mode
				if v < lowAbsolute or v > highAbsolute:
					print(f"Found Value {v} out of absolute range [{lowAbsolute}, {highPercent}] (percent range [{lowPercent}%, {highPercent}%]) during ALL mode. RGB: {pixel}. Returning True.")
					return False
	if anyMode:
		print(f"Failed to find any Values in absolute range [{lowAbsolute}, {highPercent}] (percent range [{lowPercent}%, {highPercent}%]). Returning False.")
		return False
	else: #ALL mode
		print(f"All Values found to be in absolute range [{lowAbsolute}, {highPercent}] (percent range [{lowPercent}%, {highPercent}%]). Returning True.")
		return True