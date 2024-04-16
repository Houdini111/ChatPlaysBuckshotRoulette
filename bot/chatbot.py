from threading import Thread
from time import sleep
from typing import Any
from twitchio import Message, Chatter, PartialChatter, Channel
from twitchio.ext import commands
import logging
import json
import random
import asyncio

from .secrets import getSecrets
from .vote import RunningVote, Vote, VotingTally, VotingTallyEntry, tallyVotes
from shared.util import get_event_loop
from shared.actions import Action, ShootAction, UseItemAction
from shared.log import log
from shared.consts import getShootNames, getUseNames
from overlay.overlay import getOverlay
from game.config import getChannels, getDefaultName

logger = logging.getLogger(__name__ + 'bot.chatbot')

class Chatbot(commands.Bot):
	def __init__(self):
		pass
	
	async def init(self):
		global bot
		bot = self

		self.nameVotesByUser: dict[str, str] = dict[str, str]()
		self.nameVotesByName: RunningVote[str] = RunningVote[str]()
		
		self.actionVotesByUser: dict[str, Action] = dict[str, Action]()
		self.actionVotesByAction: RunningVote[Action] = RunningVote[Action]()
		self.talliedActions: VotingTally
		
		self.awaitingActionInputs = False
		
		self.updateLeaderboardsThread = Thread(target = self.updateVoteCounts)
		self.updateLeaderboardsThread.start()
		
		await getSecrets().refresh_tokens_and_save() #Don't bother until twitch stops giving me 400s
		self.channels: dict[str, Channel] = dict[str, Channel]()
		super().__init__(
			token = getSecrets().getAccessToken(), 
			client_secret = getSecrets().getSecret(),
			prefix='#', #Unused. Listens to raw messages, not commands
			initial_channels = getChannels(),
			case_insensitive = True
		)
	
	#######
	## "Public" methods
	#######
		
	#TODO: Consolidate messages. For example "After ignoring invalid votes, the winner is"
	def openActionInputVoting(self, retrying: bool) -> None:
		self.awaitingActionInputs = True
		log(f"chatbot awaitingActionInputs: {self.awaitingActionInputs}. ID: {id(self)}")
		if not retrying:
			self.sendMessage("Voting for action now open.")
		else:
			self.sendMessage("No consensus reached. Re-opening voting.")
		
	def closeActionInputVoting(self, retrying: bool) -> None:
		self.awaitingActionInputs = False
		self.talliedActions = tallyVotes(self.actionVotesByAction)
		if not retrying:
			self.sendMessage("Voting for action closed. Deciding on winner.")
		else:
			self.sendMessage("Voting has re-closed. Deciding on winner again.")
	
	def getVotedAction(self) -> Action | None:
		self.awaitingActionInputs = False
		#Actions will require an actual winner. No tie breaker or win by default
		if not self.actionVotesByAction.hasVotes():
			return None #No action can be taken yet because no one voted. Wait longer.
		self.talliedActions = tallyVotes(self.actionVotesByAction)
		winningVote: VotingTallyEntry | None = self.talliedActions.getWinner()
		if winningVote is None:
			return None #Don't allow tiebreakers in action votes. Wait longer.
		self.sendMessage(f"Winning action of {winningVote.getVoteStr()} won with a vote count of {winningVote.getNumVotes()} ({winningVote.getPercentageStr()})")
		return winningVote.getVoteObj().getVote()
		#Do not clear votes immediately, as it might not be valid. 
	
	def removeVotedAction(self, actionToRemove: str | Action) -> None:
		self.actionVotesByAction.removeVote(actionToRemove)
		self.talliedActions.removeVote(actionToRemove)

	def clearActionVotes(self) -> None:
		self.actionVotesByAction.clear()
		self.actionVotesByUser.clear()

	def getVotedName(self) -> str:
		talliedNames: VotingTally = tallyVotes(self.nameVotesByName)
		winner: VotingTallyEntry | None = talliedNames.getNextWinner()
		if winner is None:
			self.sendMessage(f"No votes gathered. Winning name by default: \"{getDefaultName()}\"")
			return getDefaultName()
		chosenRandomly: bool = talliedNames.chosenRandomly()
		winningName: str = winner.getVoteStr()
		if chosenRandomly:
			self.sendMessage(f"{talliedNames.numNamesTied()} names tied with {winner.getNumVotes()} votes ({winner.getPercentageStr()}). Winning name chosen randomly: \"{winningName}\"")
		else:
			self.sendMessage(f"Winning name chosen with {winner.getNumVotes()} votes ({winner.getPercentageStr()}): \"{winningName}\"")
		self.clearNameVotes()
		return winningName

	def clearNameVotes(self) -> None:
		self.nameVotesByName.clear()
		self.nameVotesByUser.clear()
	
	def sendMessage(self, message: str) -> None:
		if len(self.channels) > 1:
			raise Exception("Chatbot#sendMessage cannot yet handle multiple channels")
		if len(self.channels) < 1:
			raise Exception("Chatbot#sendMessage has no channel to send the message to")
		channel: Channel = list(self.channels.values())[0]
		
		loop = get_event_loop()
		loop.create_task(self.sendMessageToChannel(channel, message))

	async def sendMessageToChannel(self, channel: Channel, message: str) -> None:
		await channel.send(message)


	#######
	## "Private" methods
	#######
	async def event_channel_joined(self, channel: Channel):
		logger.info(f"Joined channel {channel.name}")
		if channel.name not in self.channels:
			self.channels[channel.name] = channel
			self.sendMessage("Now accepting votes for the next name")

	async def event_ready(self):
		logger.info(f"Logged in as {self.nick}")

	async def event_notice(self, message: str, msg_id: str, channel):
		logger.info(f"EVENT_NOTICE: {message}")
	
	async def event_message(self, message: Message) -> None:
		author: Chatter | PartialChatter = message.author
		if author is None:
			#Self messages? Or just messages that they failed to send?
			return

		messageBody: str | None = message.content
		if messageBody is None:
			return
		messageSplit = messageBody.split(' ')
		if len(messageSplit) < 2:
			return
		command: str = messageSplit[0].lower()
		commandArgs: list[str] = messageSplit[1: 3]
		authorName: str | None = None
		if type(author) is Chatter:
			authorName = author.name
		elif type(author) is PartialChatter:
			authorName = author.name
		if authorName is None:
			return
		
		if command == "name":
			logger.debug(f"Got name vote command: \"{command} {messageSplit[1]}\"")
			self.nameVote(authorName, messageSplit[1])
		elif self.awaitingActionInputs:
			if command in getUseNames():
				logger.debug(f"Got use vote command: \"{command} {commandArgs}\"")
				self.useVote(authorName, commandArgs)
			elif command in getShootNames():
				logger.debug(f"Got shoot vote command: \"{command} {commandArgs}\"")
				self.shootVote(authorName, commandArgs)
	
	def nameVote(self, authorName: str, name: str) -> None:
		name = name[0: 5].upper().strip()

		for char in name:
			if not char.isalpha():
				return

		#TODO: Ignore names the game won't allow ("GOD", "DEALER")

		self.removeExistingVote(self.nameVotesByUser, self.nameVotesByName, authorName)
		
		logger.debug(f"Adding name vote: {name}")
		self.nameVotesByName.addAVote(name)
		self.nameVotesByUser[authorName] = name

	def removeExistingVote(self, nameDict: dict[str, Any], votes: RunningVote, authorName: str) -> None:
		if authorName in nameDict:
			oldVote: str = nameDict[authorName]
			votes.removeAVote(oldVote)

	def addActionVote(self, authorName: str, vote: Action) -> None:
		logger.debug(f"Adding action vote: {vote}")
		self.actionVotesByUser[authorName] = vote
		self.actionVotesByAction.addAVote(vote)

	def shootVote(self, authorName: str, args: list[str]) -> None:
		normalizedShootVote: ShootAction | None = self.normalizeShootVote(args)
		if normalizedShootVote is None:
			logger.debug(f"Ignoring shoot command as it could not be normalized. Args: {args}")
			return
		self.removeExistingVote(self.actionVotesByUser, self.actionVotesByAction, authorName)
		self.addActionVote(authorName, normalizedShootVote)
		
	def useVote(self, authorName: str, args: list[str]) -> None:
		normalizedUseVote: UseItemAction | None = self.normalizeUseVote(args)
		if normalizedUseVote is None:
			return
		self.removeExistingVote(self.actionVotesByUser, self.actionVotesByAction, authorName)
		self.addActionVote(authorName, normalizedUseVote)

	def normalizeShootVote(self, args: list[str]) -> ShootAction | None:
		if len(args) <= 0:
			return None
		target = args[0]
		action: ShootAction = ShootAction(target)
		if action.valid():
			return action
		return None

	def normalizeUseVote(self, args: list[str]) -> UseItemAction | None:
		argLen: int = len(args)
		if argLen <= 0:
			return None
		elif argLen > 2:
			args = args[0:2]
		
		arg1 = args[0]
		arg2 = ""
		if len(args) > 1:
			arg2 = args[1]

		useItem: UseItemAction = UseItemAction(arg1, arg2)
		if useItem.valid():
			return useItem
		return None
	
	def updateVoteCounts(self) -> None:
		while (True):
			self.updateNameLeaderboardDisplay()
			self.updateActionVotesDisplay()
			sleep(3) #TODO: configurable wait
	
	def updateNameLeaderboardDisplay(self) -> None:
		log(f"updateNameLeaderboardDisplay -> {self.nameVotesByName}")
		getOverlay().clearOldNameLeaderboard()
		if len(self.nameVotesByName) < 1:
			return
		tally: VotingTally = tallyVotes(self.nameVotesByName)
		getOverlay().drawNameVoteLeaderboard(tally.topNVotes(3))
			
	def updateActionVotesDisplay(self) -> None:
		getOverlay().clearActionVotes()
		if not self.awaitingActionInputs:
			logger.debug("Not displaying action votes as the bot isn't looking for inputs")
			return
		logger.debug(f"Tallying action votes. Action votes len: {len(self.actionVotesByAction)}")
		tally: VotingTally = tallyVotes(self.actionVotesByAction)
		getOverlay().drawActionVotes(tally.allVotes())
			
		


bot: Chatbot | None = None
def getChatbot() -> Chatbot:
	global bot
	if bot is None:
		bot = Chatbot()
		loop = get_event_loop()
		loop.run_until_complete(bot.init())
	return bot