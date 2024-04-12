import sys
import traceback
from itertools import count

tabSize = 2
def log(toPrint: str) -> None:
	logWithLevel(toPrint, stack_size() - 1)

def logWithLevel(toPrint: str, indentLevel: int) -> None:
	print(" "*tabSize*indentLevel + toPrint)

def stack_size(size:int = 2) -> int:
	frame = sys._getframe(size)

	for size in count(size):
		frame = frame.f_back
		if not frame:
			return size
	return 0