import os
from PIL import Image, ImageGrab, ImageTransform, ImageEnhance
import pytesseract
import numpy as np
import cv2
from config import getTesseractPath

def scoreboardText() -> str:
	print("### Fetching scoreboard text. Starting by grabbing image.")
	img = grabScoreBoardImage()
	print("## Scoreboard image grabbed. Preparing image for OCR.")
	img = prepareImageForOCR(img)
	print("## Scoreboard image prepared. Sending to OCR.")
	return OCR(img)

def grabScoreBoardImage() -> Image:
	left = 885
	top = 525
	right = left + 515
	bottom = top + 275
	#TODO, scale from 1440
	return ImageGrab.grab(bbox=(left, top, right, bottom))

def prepareImageForOCR(img: Image) -> Image:
	#img.save('temp_0.png')
	rotated = img.rotate(17.8, fillcolor=(0,0,0,255))
	#rotated.save('temp_1.png')
	
	src_points = np.float32([[24, 100], [468, 86], [478, 167], [38, 166]])
	dst_points = np.float32([[10, 10], [370, 10], [370, 60], [8, 60]])
	matrix = cv2.getPerspectiveTransform(src_points, dst_points)
	rotatedArray = np.asarray(rotated)
	skewedArray = []
	skewedArray = cv2.warpPerspective(rotatedArray, matrix, (480, 95))
	skewed = Image.fromarray(skewedArray)
	#skewed.save('temp_2.png')
	
	contrasted = ImageEnhance.Contrast(skewed).enhance(10)
	#contrasted.save('temp_3.png')
	
	return contrasted

def OCR(img: Image) -> str:
	pytesseract.pytesseract.tesseract_cmd = getTesseractPath()
	out = pytesseract.image_to_string(img, lang='eng', config=r'--psm 7')
	print(f"OCR RESULT: {out}")
	return