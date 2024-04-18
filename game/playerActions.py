import logging
from time import sleep

from shared.actions import Action, ShootAction, UseItemAction

from .items import getItemManager, getPlayerItemDirections, getDealerItemDirections
from .basicActions import up, down, confirm, enterDirections
from shared.consts import Target, getDealerNames, getPlayerNames, getShootNames, getUseNames
from shared.util import safeInt
from overlay.status import status

logger = logging.getLogger(__name__)

def cursorGun():
	up()
	up()
	
def cursorItem(num):
	cursorGun()
	enterDirections(getPlayerItemDirections(num, "use"))

def useGun():
	cursorGun()
	confirm()

def usePersonalItem(num):
	global currentItemPositions
	cursorItem(num)
	confirm()
	getItemManager().removeItem(num)
	status("Waiting for item use animation")
	#Is there a good way to check for which item it is to only wait as long as needed? 
	#This long of a wait might conflict with adrenaline
	sleep(6) #Has to be extra long for phone. 
	logger.info("Item use animation should be over")

def useDealerItem(num):
	down() #Move to ensure cursor is active
	enterDirections(getDealerItemDirections(num))
	confirm()
	
def chooseDealer():
	up()
	confirm()

def chooseSelf():
	down()
	confirm()

def execute(action: Action) -> bool:
	if type(action) is UseItemAction:
		return executeItemAction(action)
	elif type(action) is ShootAction:
		return executeShootAction(action)
	return False

def executeItemAction(itemAction: UseItemAction) -> bool:
	if not itemAction.valid():
		return False
		
	status("Executing use item action")
	#TODO: Check if dealer has item at location (difficult because I have to do pixel peeping that can vary based on the item it is and the item possibly in front)
	usePersonalItem(itemAction.getItemNum())
	if itemAction.getAdrenalineItemNum() != 0:
		logger.debug("Extra param given (presumably for adrenaline). Wait for adrenaline usage and movement.")
		sleep(1.5)
		useDealerItem(itemAction.getAdrenalineItemNum())
	return True

def executeShootAction(itemAction: ShootAction) -> bool:
	if not itemAction.valid():
		return False

	status("Executing shoot action")
	useGun()
	sleep(0.75) #Wait for gun move animation
	if itemAction.getTarget() == Target.SELF:
		chooseSelf()
	elif itemAction.getTarget() == Target.DEALER:
		chooseDealer()
	else:
		return False
	return True