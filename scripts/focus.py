from time import sleep
from typing import Optional
from ctypes import wintypes, windll, create_unicode_buffer

from log import log

def buckshotRouletteFocused() -> bool:
	windowName = getForegroundWindowTitle()
	if windowName == "Buckshot Roulette":
		return True

#Despite having this method, it's not recommended to tab out
#  Not everything is built around ensuring the cursor is still around. 
#  That would require a lot of pixel peeping.
#  So many things (like entering text) would break
def waitForFocus() -> None:
	if buckshotRouletteFocused():
		return
	#This method is written like this so I can write just a single message instead of spamming
	log("Waiting for game to be focused")
	while not buckshotRouletteFocused():
		sleep(0.1)


#From https://stackoverflow.com/a/58355052
def getForegroundWindowTitle() -> Optional[str]:
    hWnd = windll.user32.GetForegroundWindow()
    length = windll.user32.GetWindowTextLengthW(hWnd)
    buf = create_unicode_buffer(length + 1)
    windll.user32.GetWindowTextW(hWnd, buf, length + 1)

    return buf.value if buf.value else None