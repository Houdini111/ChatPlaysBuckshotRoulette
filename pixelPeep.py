from abc import ABC, abstractmethod

import image
import screenColors

from util import Rectangle

class Checker(ABC):
	@abstractmethod
	def passes(self) -> bool:
		pass
	
	@abstractmethod
	def getName(self) -> str:
		pass
	
	@abstractmethod
	def failureMessage(self):
		pass

class Peep(Checker):
	@abstractmethod
	def getRequirement(self) -> str:
		pass
	
	def failureMessage(self) -> str:
		return f"Pixel peep {self.getName()} fails. Requirement: {self.getRequirement()}"

class WhitePeep(Peep):
	def __init__(self, name: str, x: int, y: int, w: int, h: int):
		self.rect = Rectangle(x, y, w, h)
		self.name = name
		self.requirement = 85
	
	def passes(self) -> bool:
		return screenColors.valueOverAmountInArea(self.requirement, self.requirement)

	def getName(self) -> str:
		return self.name
	
	def getRequirement(self) -> str:
		return f"White (>={self.requirement}%)"

class BlackPeep(Peep):
	def __init__(self, name: str, x: int, y: int, w: int, h: int):
		self.rect = Rectangle(x, y, w, h)
		self.name = name
		self.requirement = 1
	
	def passes(self) -> bool:
		return screenColors.valueUnderAmountInArea(self.requirement, self.requirement)

	def getName(self) -> str:
		return self.name
	
	def getRequirement(self) -> str:
		return f"Black (<={self.requirement}%)"

class OCRScoreboardPeep(Peep):
	def __init__(self, name: str, expectedText: str):
		self.name = name
		self.expectedText = expectedText
		self.ocrTextFound = ""
	
	def passes(self) -> bool:
		self.ocrTextFound = image.scoreboardText()
		return self.ocrTextFound == self.expectedText

	def getName(self) -> str:
		return self.name
	
	def getRequirement(self) -> str:
		return f"Text to match {self.expectedText}. Found {self.ocrTextFound})."

class Peeper():
	#TODO: Visual Studio doesn't like having a Peeper in the constructor for a Peeper, even if it's optional
	def __init__(self, name: str, *checkers: Checker):
		self.name = name
		self.checkers = list(checkers)
		self.failedChecker = None
	
	def failedChecker(self):
		return self.failedPeep
	
	def failureMessage(self) -> str:
		return f"Peeper {self.name} fails because of -> {self.failedChecker().failureMessage()}";
	
	def passes(self) -> bool:
		for checker in self.checkers.values():
			if not checker.passes():
				self.failedChecker = checker
				print(self.failureMessage())
				return False
		return True