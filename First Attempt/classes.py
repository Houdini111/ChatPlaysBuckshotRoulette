from enum import Enum

class Action(Enum):
	GUN=1
	ITEM=2

class ItemPos(Enum):
	TOP_LEFT=1
	MIDDLE_TOP_LEFT=2
	MIDDLE_TOP_RIGHT=3
	TOP_RIGHT=4
	BOTTOM_LEFT=5
	MIDDLE_BOTTOM_LEFT=6
	MIDDLE_BOTTOM_RIGHT=7
	BOTTOM_RIGHT=8
	
class Resolution:
	def __init__(self, h: int, w: int):
		self.height = h
		self.width = w 

class Point():
	def __init__(self, x: float, y: float, originIsTopLeft: bool):
		self.originIsTopLeft = originIsTopLeft
		self.x = x
		self.y = y
	
	def topLeftOrigin(self, res: Resolution):
		if self.originIsTopLeft:
			return self
		else:
			return self.flippedOrigin(res)
	
	def bottomLeftOrigin(self, res: Resolution):
		if self.originIsTopLeft:
			return self.flippedOrigin(res)
		else:
			return self
		
	def flippedOrigin(self, res: Resolution):
		return Point(self.x, res.height - self.y, not self.originIsTopLeft) 
	