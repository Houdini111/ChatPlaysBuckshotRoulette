from datetime import datetime
import decimal
from typing import Callable
import tkinter as tk

class Countdown():
	def __init__(self, x1440: int, y1440: int, fontSize: float, updateFps: float, startTime: int, decimals: int, maxStringLength: int, drawText1440: Callable, root: tk.Tk, canvas: tk.Canvas):
		self.x1440: int = x1440
		self.y1440: int = y1440
		self.fontSize: float = fontSize
		self.updateFps: float = updateFps
		self.secondsBetweenUpdates: float = 1.0/self.updateFps
		self.startingTime: int = startTime
		self.maxStringLength: int = maxStringLength
		self.decimals: int = decimals
		self.root: tk.Tk = root
		self.canvas: tk.Canvas = canvas
		self.drawText1440: Callable = drawText1440
		self.go: bool = False
		self.initElements()
		
	def initElements(self):
		self.textElem = self.drawText1440("", self.x1440, self.y1440, self.fontSize, self.canvas, anchor = "s")
		
	def start(self):
		self.go = True
		self.startedTime: float = datetime.now().timestamp()
		self.currentTime = self.startedTime
		self.lastTime: float = self.startedTime
		self.timeLeft = self.startingTime
		self.update()
	
	def end(self):
		self.go = False
	
	def frameSetup(self):
		now: float = datetime.now().timestamp()
		self.lastTime: float = self.currentTime
		self.currentTime: float = now

	def delta(self):
		return self.currentTime - self.lastTime

	def secondsToNextUpdate(self):
		secondsToNextUpdate: float = self.secondsBetweenUpdates - self.delta()
		return secondsToNextUpdate

	def update(self):
		self.frameSetup()
		if not self.go:
			return

		secondsToWait: float = self.secondsToNextUpdate()
		msToWait: float = secondsToWait * 1000
		flooredMsToWait: int = int(msToWait)
		
		timeLeft: float = self.startingTime - (self.currentTime - self.startedTime)
		if timeLeft < 0:
			timeLeft = 0
		self.render(timeLeft)
		
		if timeLeft > 0:
			self.root.after(flooredMsToWait, self.update)
		
	def render(self, timeToRender: float):
		formatted: str = self.formatTime(timeToRender)
		self.canvas.itemconfig(self.textElem, text=formatted)
		
	def formatTime(self, timeToFormat: float):
		rounded: str = str(round(timeToFormat, self.decimals))
		if self.decimals <= 0:
			roundedSplit: list[str] = rounded.split('.')
			return roundedSplit[0]
		
		if '.' not in rounded:
			rounded += '.'
		
		decimalPoints: int = 0
		roundedSplit: list[str] = rounded.split('.')
		if len(roundedSplit) < 2:
			decimalPoints = 0
		else:
			decimalPoints = len(roundedSplit[1])
		
		while decimalPoints < self.decimals:
			rounded += '0'
			decimalPoints += 1
			
		#Cut down to max string length
		limited: str = rounded[:self.maxStringLength]
		#If it has a trailing period, remove that too
		if limited.endswith('.'):
			limited = limited[:-1]

		return limited