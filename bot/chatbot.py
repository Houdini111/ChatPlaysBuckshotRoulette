from threading import Thread
from time import sleep, thread_time_ns
from typing import Any
from twitchio import Message, Chatter, PartialChatter, Channel
from twitchio.ext import commands
from copy import deepcopy
from unidecode import unidecode
import logging
import json
import random
import asyncio

from .secrets import getSecrets
from .vote import RunningVote, Vote, VotingTally, VotingTallyEntry, tallyVotes
from shared.util import run_task
from shared.actions import Action, ShootAction, UseItemAction
from shared.consts import getShootNames, getUseNames, getDealerNames, getPlayerNames, getMaxNameLength
from shared.config import getChannels, getDefaultName, getInstructionsCooldown
from overlay.overlay import getOverlay

logger = logging.getLogger(__name__)

class Chatbot(commands.Bot):
	def __init__(self):
		print("Running with init")
		global bot
		bot = self
		self.prefix = "!" #TODO: Make confugrable
		
		self.nameVotesByUser: dict[str, str] = dict[str, str]()
		self.nameVotesByName: RunningVote[str] = RunningVote[str]()
		
		self.actionVotesByUser: dict[str, Action] = dict[str, Action]()
		self.actionVotesByAction: RunningVote[Action] = RunningVote[Action]()
		self.talliedActions: VotingTally
		
		self.awaitingActionInputs = False
		
		self.updateLeaderboardsThread = Thread(target = self.updateVoteCounts)
		self.updateLeaderboardsThread.start()
		
		self.instructionsCooldownS: int = getInstructionsCooldown()
		self.instructionsCooldownNs: int = self.instructionsCooldownS * 1000000000
		self.instructionsLastCalled: int = thread_time_ns()
		self.instructionsCommandStr = self.prefix + "instructions"

		self.initMessageMaxLen()
		
		self.channels: dict[str, Channel] = dict[str, Channel]()
		super().__init__(
			token = getSecrets().getAccessToken(), 
			client_secret = getSecrets().getSecret(),
			prefix= self.prefix,
			initial_channels = getChannels(),
			case_insensitive = True,
		)
	
	#######
	## "Public" methods
	#######

	#TODO: Consolidate messages. For example "After ignoring invalid votes, the winner is"
	def openActionInputVoting(self, retrying: bool) -> None:
		self.awaitingActionInputs = True
		logger.debug(f"chatbot awaitingActionInputs: {self.awaitingActionInputs}. ID: {id(self)}")
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
		
		logger.debug(f"Winning vote [{winningVote.getVoteObj()}] has adrenaline percent of {winningVote.getVoteObj().getAdrenalinePercent() * 100}%. Is adrenaline item: {winningVote.getVoteObj().isAdrenalineItem()}")
		if winningVote.getVoteObj().isAdrenalineItem():
			winningAdrenalineVote: int = self.talliedActions.getWinningAdrenalineItemVote()
			winningVote: VotingTallyEntry = deepcopy(winningVote)
			winningVote.adrenalineItemVote = winningAdrenalineVote
		self.sendMessage(f"Winning action of [{str(winningVote.getVoteObj().getVote()).upper()}] won with a vote count of {winningVote.getNumVotes()} ({winningVote.getPercentageStr()})")
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
		logger.debug(f"Name dict lens after clear: {len(self.nameVotesByName)} {len(self.nameVotesByName)}")
	
	def sendMessage(self, message: str) -> None:
		if len(self.channels) > 1:
			raise Exception("Chatbot#sendMessage cannot yet handle multiple channels")
		if len(self.channels) < 1:
			raise Exception("Chatbot#sendMessage has no channel to send the message to")
		channel: Channel = list(self.channels.values())[0]
		
		logger.debug(f"Creating event loop task to send a chatbot message to channel \"{channel.name}\": ||{message}||")
		logger.debug(f"Getting an event loop to send message to channel \"{channel.name}\": ||{message}||")
		
		run_task(lambda: self.sendMessageToChannel(channel, message))

	async def sendMessageToChannel(self, channel: Channel, message: str) -> None:
		logger.debug(f"Sending message to channel \"{channel.name}\": ||{message}||")
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
		messageBody = messageBody[ :self.maxMessageLen] #Truncate to the maximum message length to improve string .split() performance
		
		if messageBody.startswith(self.prefix + "instructions"):
			await self.printInstructions()
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
		name = unidecode(name)
		name = name.replace(" ", "")
		name = name[0: getMaxNameLength()].upper().strip()

		#Note: Does not like the following :
		# "ー" like in "ビール". Converts to "-", which is non-alpha

		for char in name:
			if not char.isalpha(): 
				logger.debug(f"Voted name \"{name}\" contains non alpha char \"{char}\". Name rejected.")
				return

		#TODO: Ignore names the game won't allow ("GOD", "DEALER")

		self.removeExistingVote(self.nameVotesByUser, self.nameVotesByName, authorName)
		
		logger.debug(f"Adding name vote: {name}")
		self.nameVotesByName.addAVote(name)
		self.nameVotesByUser[authorName] = name
		logger.debug(f"Added name vote for {authorName}: \"{name}\"")

	def removeExistingVote(self, voteDict: dict[str, Any], votes: RunningVote, authorName: str) -> None:
		if authorName in voteDict:
			oldVote: Any = voteDict[authorName]
			logger.debug(f"User \"{authorName}\" already voted. Removing their previous vote of \"{oldVote}\"")
			votes.removeAVote(oldVote)

	def addActionVote(self, authorName: str, vote: Action) -> None:
		logger.debug(f"Adding action vote: {vote}")
		self.actionVotesByUser[authorName] = vote
		self.actionVotesByAction.addAVote(vote)
		logger.debug(f"Added action vote for {authorName}: \"{vote}\"")

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
		logger.debug(f"Normalizing Use Vote with args: {args}")
		argLen: int = len(args)
		if argLen <= 0:
			logger.debug("No arguments found for use vote. Invalid.")
			return None
		elif argLen > 2:
			args = args[0:2]
		
		arg1 = args[0]
		arg2 = ""
		if len(args) > 1:
			arg2 = args[1]

		logger.debug(f"Parsed normalized Use Vote args of: [{arg1}] and [{arg2}]")

		useItem: UseItemAction = UseItemAction(arg1, arg2)
		if useItem.valid():
			logger.debug(f"Use Item Action created was valid: {useItem}")
			return useItem
		logger.debug(f"Use Item Action was Invalid: {useItem}")
		return None
	
	def updateVoteCounts(self) -> None:
		while (True):
			self.updateNameLeaderboardDisplay()
			self.updateActionVotesDisplay()
			sleep(3) #TODO: configurable wait
	
	def updateNameLeaderboardDisplay(self) -> None:
		logger.info(f"Updating name votes -> {self.nameVotesByName}")
		getOverlay().clearOldNameLeaderboard()
		if len(self.nameVotesByName) < 1:
			return
		tally: VotingTally = tallyVotes(self.nameVotesByName)
		getOverlay().drawNameVoteLeaderboard(tally.topNVotes(3))
			
	def updateActionVotesDisplay(self) -> None:
		logger.info("Updating action votes")
		getOverlay().clearActionVotes()
		if not self.awaitingActionInputs:
			logger.debug("Not displaying action votes as the bot isn't looking for inputs")
			return
		logger.debug(f"Tallying action votes. Action votes len: {len(self.actionVotesByAction)}")
		tally: VotingTally = tallyVotes(self.actionVotesByAction)
		getOverlay().drawActionVotes(tally.allVotes(), tally.getAdrenalineItemVotes())

	async def printInstructions(self, ctx: commands.Context | None = None):
		logger.info("Instructions command called")
		nowCalled: int = thread_time_ns()
		elapsedNs: int = nowCalled - self.instructionsLastCalled
		cooldownRemaining: int = self.instructionsCooldownNs - elapsedNs
		if cooldownRemaining <= 0:
			logger.info(f"Instructions command was called but was still on cooldown. Cooldown: {self.instructionsCooldownNs}ns Elapsed: {elapsedNs} Remaining: {cooldownRemaining}")
			return
		
		msg: str = "To vote on a name write: \"name\" followed by your voted name. \
				 To vote to shoot someone use \"shoot\" followed by either \"dealer\" or \"self\". \
				 To vote to use an item write \"use\" and the item's position (1 through 8, left to right, top to bottom). \
				 If you vote for an adrenaline your message should also include the dealer's item to use, for example: \"use 2 3\" to use the adrenaline in position 2 to use the dealers item in position 3."
				 
		if ctx is None:
			self.sendMessage(msg)
		else:
			await ctx.send(msg)
			
	def initMessageMaxLen(self) -> None:
		#This could have been simply hard coded but I wanted it to be able to handle me making changes elsewhere.
		#  But I'm calculating once and storing it so it's not a big deal

		shootMaxLen: int = len(max(getShootNames(), key=len))
		useMaxLen: int = len(max(getUseNames(), key=len))
		nameLen: int = len("name ")
		votePrefixMaxLen: int = max(shootMaxLen, useMaxLen, nameLen)
		
		dealerNameValueLen: int = len(max(getDealerNames(), key=len))
		playerNameValueLen: int = len(max(getPlayerNames(), key=len))
		targetValueLen: int = max(dealerNameValueLen, playerNameValueLen)
		useValueLen: int = 4 #Two 1 digit numbers separated from each other and the key by a space 
		nameValueLen: int = getMaxNameLength() #6 character limit from the game
		voteValueMaxLen: int = max(targetValueLen, useValueLen, nameValueLen)

		voteMaxLen: int = votePrefixMaxLen + voteValueMaxLen

		instructionsCommandLen: int = len(self.instructionsCommandStr)
		
		self.maxMessageLen: int = max(voteMaxLen, instructionsCommandLen)
		

bot: Chatbot | None = None
def getChatbot() -> Chatbot:
	global bot
	if bot is None:
		bot = Chatbot()
	return bot

def createAndStartChatbot():
	#asyncio.run destroys the loop after
	asyncio.run(getSecrets().refresh_tokens_and_save())
	
	#TwitchIO bots expect get_event_loop to succeed, so I need to prepare for that. 
	loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)
	getChatbot()
	getChatbot().run()

#TwitchIO REALLY doesn't like being run in asyncio. It expects free access to its own asyncio loop, so it needs to be in its own thread
def createAndStartChatbotThread():
	botThread = Thread(target = createAndStartChatbot)
	botThread.start()