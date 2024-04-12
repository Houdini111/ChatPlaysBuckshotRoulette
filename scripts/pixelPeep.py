from abc import ABC, abstractmethod

from image import scoreboardText
from screenColors import valuesInRangeInRect

from util import Rectangle
from log import log

class Checker(ABC):
	@abstractmethod
	def passes(self) -> bool:
		pass
	
	@abstractmethod
	def getName(self) -> str:
		pass
	
	@abstractmethod
	def failureMessage(self) -> str:
		pass

class Peep(Checker):
	@abstractmethod
	def getRequirement(self) -> str:
		pass
	
	def failureMessage(self) -> str:
		return f"Pixel peep {self.getName()} fails. Requirement: {self.getRequirement()}"

class RangePeep(Peep):
	def __init__(self, name: str, lowPercent: float, highPercent: float, anyMode: bool, x: int, y: int, w: int, h: int):
		self.rect = Rectangle(x, y, w, h)
		self.validateRect(self.rect)
		if lowPercent < 0 or lowPercent > highPercent:
			raise ValueError(f"Requested low value below 0% or higher than high percent for Peep: {name}. Low percent: {lowPercent} High Percent: {highPercent}")
		if highPercent > 100: #No need to check for mixed up values again
			raise ValueError(f"Requested high value above 100% zero for Peep: {name}. High Percent: {highPercent}")
		self.lowPercent = lowPercent
		self.highPercent = highPercent
		self.anyMode = anyMode
		self.name = name
	
	def passes(self) -> bool:
		return valuesInRangeInRect(self.lowPercent, self.highPercent, self.anyMode, self.rect)

	def getName(self) -> str:
		return self.name
	
	def getRequirement(self) -> str:
		return f"Range [{self.lowPercent}, {self.highPercent}]%"
	
	def validateRect(self, rect: Rectangle) -> bool:
		if rect.x < 0 or rect.x > 2560:
			raise ValueError(f"X COORDINATE ({rect.y}) INVALID")
		if rect.y < 0 or rect.y > 1440:
			raise ValueError(f"Y COORDINATE ({rect.y}) INVALID")
		if rect.x + rect.w > 2560:
			raise ValueError(f"RIGHT EDGE ({rect.x + rect.w}) INVALID")
		if rect.y + rect.h > 1440:
			raise ValueError(f"LEFT EDGE ({rect.y + rect.h}) INVALID")
		return True


class AnyWhitePeep(RangePeep):
	def __init__(self, name: str, x: int, y: int, w: int, h: int):
		super().__init__(name, 85, 100, True, x, y, w, h)

	def getRequirement(self) -> str:
		return f"White (>={self.lowPercent}%)"

class AllBlackPeep(RangePeep):
	def __init__(self, name: str, x: int, y: int, w: int, h: int):
		super().__init__(name, 0, 1, False, x, y, w, h)

	def getRequirement(self) -> str:
		return f"Black (<={self.lowPercent}%)"


class OCRScoreboardPeep(Peep):
	def __init__(self, name: str, expectedText: str):
		self.name = name
		self.expectedText = expectedText
		self.ocrTextFound = ""
	
	def passes(self) -> bool:
		self.ocrTextFound = scoreboardText()
		return self.ocrTextFound == self.expectedText

	def getName(self) -> str:
		return self.name
	
	def getRequirement(self) -> str:
		return f"Text to match {self.expectedText}. Found {self.ocrTextFound})."

class Peeper(Checker):
	def __init__(self, name: str, *checkers: Checker):
		self.name = name
		self.checkers = list(checkers)
		self.failedChecker: Checker
	
	def getName(self) -> str:
		return self.name

	def failureMessage(self) -> str:
		failedMessage: str = "No Fail Message Found"
		if self.failedChecker is not None:
			failedMessage = self.failedChecker.failureMessage()
		return f"Peeper {self.name} fails because of -> {failedMessage}";
	
	def passes(self) -> bool:
		for checker in self.checkers:
			if not checker.passes():
				self.failedChecker = checker
				log(self.failureMessage())
				return False
		return True