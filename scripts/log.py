import logging
import sys
import traceback
from itertools import count

logger = logging.getLogger(__name__ + 'scripts.log')

tabSize = 2

def log(toPrint: str, logLevel: int = logging.INFO) -> None:
	logWithIndentation(toPrint, stack_size() - 1, logLevel)

def logWithIndentation(toPrint: str, indentLevel: int, logLevel: int = logging.INFO) -> None:
	logger.info(" "*tabSize*indentLevel + toPrint)

def stack_size(size:int = 2) -> int:
	frame = sys._getframe(size)

	for size in count(size):
		frame = frame.f_back
		if not frame:
			return size
	return 0