from typing import Any
from twitchio import Message, Chatter, PartialChatter, Channel
from twitchio.ext import commands
import logging
import json
import random
import asyncio

from scripts.util import get_event_loop

from .secrets import getSecrets
from scripts.config import getChannels, getDefaultName

logger = logging.getLogger(__name__ + 'bot.chatbot')


class VoteResult():
	def __init__(self, winners: list[str], winningVotes: int, totalVotes: int, byDefault: bool):
		self.winners = winners
		self.winningVotes = winningVotes
		self.byDefault = byDefault
		self.totalVotes = totalVotes
		if self.tied():
			self.winner = random.choice(self.winners)
		else:
			self.winner = self.winners[0]
	
	def winnerCount(self) -> int:
		return len(self.winners)

	def tied(self) -> bool: 
		return len(self.winners) > 1

	def getWinner(self) -> str:
		return self.winner

	def getAllWinners(self) -> list[str]:
		return self.winners
	
	def getWinningVotes(self) -> int:
		return self.winningVotes
	
	def wonByDefault(self) -> bool:
		return self.byDefault
	
	def winningPercentage(self) -> str:
		return str(round(float(self.winningVotes)/self.totalVotes*100))+"%"

class Chatbot(commands.Bot):
	def __init__(self):
		pass
	
	async def init(self):
		global bot
		bot = self

		self.useNames = ["use", "item", "consume", "take"]
		self.shootNames = ["shoot", "shot", "attack", "hit", "target"]
		self.dealerNames = ["dealer", "them", "guy", "other"]
		self.playerNames = ["self", "me", "player", "i", "myself"]

		self.nameVotesByUser: dict[str, str] = {}
		self.nameVotesByName: dict[str, int] = {}
		
		self.actionVotesByUser: dict[str, str] = {}
		self.actionVotesByAction: dict[str, int] = {}
		self.modifiedActionVotesByAction: dict[str, int] = {}
		
		self.awaitingActionInputs = False

		#await getSecrets().refresh_tokens_and_save() #Don't bother until twitch stops giving me 400s
		self.channels: dict[str, Channel] = {}
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
	def openActionInputVoting(self, retrying: bool) -> None:
		self.awaitingActionInputs = True
		self.modifiedActionVotesByAction.clear()
		if not retrying:
			self.sendMessage("Voting for action now open.")
		else:
			self.sendMessage("No consensus reached. Re-opening voting.")
		
	def closeActionInputVoting(self, retrying: bool) -> None:
		self.awaitingActionInputs = False
		self.modifiedActionVotesByAction = self.actionVotesByAction.copy()
		if not retrying:
			self.sendMessage("Voting for action closed. Deciding on winner.")
		else:
			self.sendMessage("Voting has re-closed. Deciding on winner again.")
	
	def getVotedAction(self) -> str:
		self.awaitingActionInputs = False
		#Actions will require an actual winner. No tie breaker or win by default
		if len(self.actionVotesByAction) < 1:
			return "" #No action can be taken yet because no one voted. Wait longer.
		voteResult: VoteResult = self.tallyVote(self.modifiedActionVotesByAction, "")
		if voteResult.wonByDefault():
			return ""
		elif voteResult.tied():
			return ""
		self.sendMessage(f"Winning action of {voteResult.getWinner()} won with a vote count of {voteResult.getWinningVotes()} ({voteResult.winningPercentage()}")
		return voteResult.getWinner()
		#Do not clear votes immediately, as it might not be valid. 
	
	def removeVotedAction(self, actionToRemove: str) -> None:
		self.modifiedActionVotesByAction.pop(actionToRemove)

	def clearActionVotes(self) -> None:
		self.actionVotesByAction.clear()
		self.actionVotesByUser.clear()
		self.modifiedActionVotesByAction.clear()

	def getVotedName(self) -> str:
		voteResult: VoteResult = self.tallyVote(self.nameVotesByName, getDefaultName())
		
		winningName: str = voteResult.getWinner()
		if voteResult.wonByDefault():
			self.sendMessage(f"No votes gathered. Winning name by default: \"{winningName}\"")
		elif voteResult.tied():
			self.sendMessage(f"{voteResult.winnerCount()} names tied with {voteResult.getWinningVotes()} votes ({voteResult.winningPercentage()}). Winning name chosen randomly: \"{winningName}\"")
		else:
			self.sendMessage(f"Winning name chosen with {voteResult.getWinningVotes()} votes ({voteResult.winningPercentage()}): \"{winningName}\"")
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
		loop.run_until_complete(self.sendMessageToChannel(channel, message))

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

		messageBody = message.content
		messageSplit = messageBody.split(' ')
		if len(messageSplit) < 2:
			return
		command = messageSplit[0].lower()
		commandArgs = messageSplit[1: 3]
		authorName: str = author.name
		if command == "name":
			self.nameVote(authorName, messageSplit[1])
		elif self.awaitingActionInputs:
			if command in self.useNames:
				self.useVote(authorName, commandArgs)
			elif command in self.shootNames:
				self.shootVote(authorName, commandArgs)
	
	def nameVote(self, authorName: str, name: str) -> None:
		name = name[0: 5].upper().strip()

		for char in name:
			if not char.isalpha():
				return

		#TODO: Ignore names the game won't allow ("GOD", "DEALER")

		if authorName in self.nameVotesByUser:
			previousVote = self.nameVotesByUser[authorName]
			self.nameVotesByName[previousVote] -= 1
		
		self.vote(self.nameVotesByName, name)
		self.nameVotesByUser[authorName] = name
		print(f"Name Votes By User: {json.dumps(self.nameVotesByUser)}")
		print(f"Name Votes By Name: {json.dumps(self.nameVotesByName)}")
	
	def vote(self, dictToVoteOn: dict[str, int], vote: str) -> None:
		if vote in dictToVoteOn:
			dictToVoteOn[vote] += 1
		else:
			dictToVoteOn[vote] = 1
		print(f"Action Votes By User: {json.dumps(self.actionVotesByUser)}")
		print(f"Action Votes By Action: {json.dumps(self.actionVotesByAction)}")

	def removeExistingVote(self, authorName: str) -> None:
		if authorName in self.actionVotesByUser:
			oldVote: str = self.actionVotesByUser[authorName]
			self.actionVotesByAction[oldVote] -= 1

	def addActionVote(self, authorName: str, vote: str) -> None:
		self.actionVotesByUser[authorName] = vote
		self.vote(self.actionVotesByAction, vote)

	def shootVote(self, authorName: str, args: list[str]) -> None:
		normalizedShootVote: str | None = self.normalizeShootVote(args)
		if normalizedShootVote is None:
			return
		self.removeExistingVote(authorName)
		self.addActionVote(authorName, normalizedShootVote)
		
	def useVote(self, authorName: str, args: list[str]) -> None:
		normalizedUseVote: str | None = self.normalizeUseVote(args)
		if normalizedUseVote is None:
			return
		self.removeExistingVote(authorName)
		self.addActionVote(authorName, normalizedUseVote)

	def normalizeShootVote(self, args: list[str]) -> str | None:
		if len(args) <= 0:
			return None
		target = args[0]
		if target in self.dealerNames:
			return f"{self.shootNames[0]} {self.dealerNames[0]}"
		elif target in self.playerNames:
			return f"{self.shootNames[0]} {self.playerNames[0]}"
		return None

	def normalizeUseVote(self, args: list[str]) -> str | None:
		argLen: int = len(args)
		if argLen <= 0:
			return None
		elif argLen > 2:
			args = args[0:2]
		
		for arg in args:
			if not arg.isdigit():
				return None
			parsedArg = int(arg)
			if parsedArg < 0 or parsedArg > 8:
				return None
		normalizedArgs = args[0]
		if argLen > 1:
			normalizedArgs += " " + args[1]
		return f"{self.useNames[0]} {normalizedArgs}"
	
	def tallyVote(self, voteCount: dict[str, int], defaultOption: str) -> VoteResult:
		winningVotes: list[str] = [ defaultOption ]
		highestCount: int = -1
		totalCount: int = 0
		for voteOption in voteCount:
			count = voteCount[voteOption]
			totalCount += count
			if count > highestCount:
				winningVotes = [voteOption]
				highestCount = count
			elif voteCount[voteOption] == highestCount:
				winningVotes.append(voteOption)
		byDefault = highestCount < 0
		if highestCount < 0:
			highestCount = 0
		return VoteResult(winningVotes, highestCount, totalCount, byDefault)


bot: Chatbot | None = None
def getChatbot() -> Chatbot:
	global bot
	if bot is None:
		bot = Chatbot()
		loop = get_event_loop()
		loop.run_until_complete(bot.init())
	return bot