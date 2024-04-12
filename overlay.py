import tkinter as tk
from PIL import ImageTk, Image
import pyautogui
from time import sleep
from threading import Thread
import math

from util import resizePointFrom1440p


displayW, displayH = pyautogui.size()

root: tk.Tk = tk.Tk()
root.overrideredirect(True)
canvas = tk.Canvas(width=displayW, height=displayH, bg="green")
canvas.pack(expand=tk.YES, fill=tk.BOTH)

root.wm_attributes("-topmost", True)
root.wm_attributes("-disabled", True)
root.wm_attributes("-transparentcolor", "green")

fontSize = math.ceil(80 * (float(displayH) / 1440)) #80 is the size I want at 1440p
overlayFont = ("Arial", fontSize, "bold")
playerNumGridPositions = {
	1: [700, 550],	
	2: [900, 550],
	3: [1625, 550],
	4: [1850, 550],
	5: [575, 800],
	6: [850, 800],
	7: [1700, 800],
	8: [1975, 800]
}

def draw_text_1440(canvas: tk.Canvas, text: str, x1440: int, y1440: int) -> None:
	realX, realY = resizePointFrom1440p(x1440, y1440)
	canvas.create_text(realX, realY, text = text, fill="white", font=overlayFont)

def drawNumberGrid(canvas: tk.Canvas, numbersToDraw: list[int]) -> None:
	for i in numbersToDraw:
		if i < 1 or i > 8:
			continue
		pos = playerNumGridPositions[i]
		draw_text_1440(canvas, str(i), pos[0], pos[1])


def closeRootAfterATime(toClose: tk.Tk, canvas: tk.Canvas) -> None:
	canvas.create_rectangle(0, 0, 2560, 1440, width = 10, outline="white")
	drawNumberGrid(canvas, list(range(1, 9)))
	print("Starting close wait")
	sleep(5)
	print("After close wait, sending quit command")
	toClose.destroy()

def createHandlerThread() -> None:
	handlerThread = Thread(target = closeRootAfterATime, args=([root, canvas]))
	handlerThread.daemon = True
	handlerThread.start()

createHandlerThread()
tk.mainloop()