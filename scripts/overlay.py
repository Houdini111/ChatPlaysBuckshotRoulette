import tkinter as tk
from PIL import ImageTk, Image
import pyautogui
from time import sleep
from threading import Thread
import math

from .util import resizePointFrom1440p

class Overlay():
	def __init__(self):
		self.displayW, self.displayH = pyautogui.size()
		self.root: tk.Tk = tk.Tk()
		self.root.title("Chat Plays Buckshot Roulette - Chat Overlay")
		self.root.wm_attributes("-fullscreen", True)
		self.root.wm_attributes("-transparentcolor", "green")

		self.canvas = tk.Canvas(width = self.displayW, height = self.displayH, bg="green")
		self.canvas.pack(expand=tk.YES, fill=tk.BOTH)
		
		self.optionsFontSize = math.ceil(80 * (float(self.displayH) / 1440)) #80 is the size I want at 1440p
		
		self.playerNumGridPositions = {
			1: [650, 500],	
			2: [875, 500],
			3: [1600, 500],
			4: [1825, 500],
			5: [525, 750],
			6: [825, 750],
			7: [1675, 750],
			8: [1950, 750]
		}
		
		self.draw_text_1440("Chat Overlay Active", 10, 10, 40)
		self.drawNumberGrid(list(range(1, 9)))
	
	def run(self) -> None:
		tk.mainloop()
	
	def stop(self) -> None:
		self.root.destroy()

	def draw_text_1440(self, text: str, x1440: int, y1440: int, fontSize: float, bold: bool = True) -> None:
		realX, realY = resizePointFrom1440p(x1440, y1440)
		font = ("Arial", fontSize)
		if bold:
			font += ("bold", )
		self.canvas.create_text(realX, realY, text = text, fill = "white", font = font, anchor = "nw")

	def drawNumberGrid(self, numbersToDraw: list[int]) -> None:
		for i in numbersToDraw:
			if i < 1 or i > 8:
				continue
			pos = self.playerNumGridPositions[i]
			self.draw_text_1440(str(i), pos[0], pos[1], self.optionsFontSize)