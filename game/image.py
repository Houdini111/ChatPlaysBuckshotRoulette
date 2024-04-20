import logging
import os
import time
from PIL import Image, ImageGrab, ImageTransform, ImageEnhance
import pytesseract
import numpy as np
import cv2

from shared.config import getTesseractPath, getOutputOcrImages

logger = logging.getLogger(__name__)

ocrImageDir: str = "ocr_debug_images"

callStartEpocSeconds: int = 0
def scoreboardText() -> str:
	global callStartEpocSeconds
	logger.debug("Fetching scoreboard text. Starting by grabbing image.")
	callStartEpocSeconds = int(time.time())
	img = grabScoreBoardImage()
	logger.debug("Scoreboard image grabbed. Preparing image for OCR.")
	img = prepareImageForOCR(img)
	logger.debug("Scoreboard image prepared. Sending to OCR.")
	return OCR(img)

def grabScoreBoardImage() -> Image:
	left = 885
	top = 525
	right = left + 515
	bottom = top + 275
	#TODO, scale from 1440
	return ImageGrab.grab(bbox=(left, top, right, bottom))

def prepareImageForOCR(raw: Image) -> Image:
	if not os.path.isdir(ocrImageDir):
		os.makedirs(ocrImageDir)
	if getOutputOcrImages():
		saveOcrImage(raw, "raw", 0)
	rotated = raw.rotate(17.8, fillcolor=(0,0,0,255))
	if getOutputOcrImages():
		saveOcrImage(rotated, "rotated", 1)
	
	src_points = np.float32([[24, 100], [468, 86], [478, 167], [38, 166]])
	dst_points = np.float32([[10, 10], [370, 10], [370, 60], [8, 60]])
	matrix = cv2.getPerspectiveTransform(src_points, dst_points)
	rotatedArray = np.asarray(rotated)
	skewedArray = list()
	skewedArray = cv2.warpPerspective(rotatedArray, matrix, (480, 95))
	skewed = Image.fromarray(skewedArray)
	if getOutputOcrImages():
		saveOcrImage(skewed, "skewed", 2)
	
	contrasted = ImageEnhance.Contrast(skewed).enhance(10)
	if getOutputOcrImages():
		saveOcrImage(contrasted, "contrasted", 4)
	
	return contrasted
	
def OCR(img: Image) -> str:
	pytesseract.pytesseract.tesseract_cmd = getTesseractPath()
	out = pytesseract.image_to_string(img, lang='eng', config=r'--psm 7')
	logger.info(f"OCR RESULT: {out}")
	return out


def saveOcrImage(img: Image, title: str, num: int):
	fileName: str = f"{callStartEpocSeconds}_OCR_{num}_{title}.png"
	img.save(os.path.join(ocrImageDir, fileName))