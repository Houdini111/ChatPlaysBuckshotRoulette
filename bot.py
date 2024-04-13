from typing import Any
from twitchio import Message, Chatter, PartialChatter
from twitchio.ext import commands
import logging
import json
import random

from bot.secrets import getSecrets
from scripts.config import getChannels, getDefaultName

logger = logging.getLogger(__name__ + '.bot')

class Chatbot(commands.Bot):
	def __init__(self):
		self.useNames = ["use", "item", "consume", "take"]
		self.shootNames = ["shoot", "shot", "attack", "hit", "target"]
		self.dealerNames = ["dealer", "them", "guy", "other"]
		self.playerNames = ["self", "me", "player", "i"]

		self.nameVotesByUser: dict[str, str] = {}
		self.nameVotesByName: dict[str, int] = {}
		
		self.actionVotesByUser: dict[str, str] = {}
		self.actionVotesByAction: dict[str, int] = {}
		
		self.awaitingActionInputs = False

		super().__init__(
			token = getSecrets().getAccessToken(), 
			client_secret = getSecrets().getSecret(),
			prefix='#', #Unused. Listens to raw messages, not commands
			initial_channels = getChannels(),
			case_insensitive = True
		)
	
	def awaitActionInputs(self) -> None:
		self.awaitingActionInputs = True
	
	def stopAwaitingActionInputs(self) -> None:
		self.awaitingActionInputs = False
		self.actionVotesByAction.clear()
		self.actionVotesByUser.clear()

	def getVotedName(self) -> str:
		if len(self.nameVotesByName) < 1:
			return getDefaultName()
		highestNames: list[str] = [ getDefaultName() ]
		highestCount: int = -1
		for name in self.nameVotesByName:
			count = self.nameVotesByName[name]
			if count > highestCount:
				highestNames = [name]
				highestCount = count
			elif self.nameVotesByName[name] == highestCount:
				highestNames.append(name)
		self.clearNameVotes()
		if len(highestNames) > 1:
			#Tie breaker, choose random
			return random.choice(highestNames)
		return highestNames[0]

	def clearNameVotes(self) -> None:
		self.nameVotesByName.clear()
		self.nameVotesByUser.clear()


	async def event_ready(self):
		logger.info(f"Logged in as {self.nick}")

	async def event_notice(self, message: str, msg_id: str, channel):
		logger.info("EVENT_NOTICE: {message}")
	
	async def event_message(self, message: Message) -> None:
		messageBody = message.content
		messageSplit = messageBody.split(' ')
		if len(messageSplit) < 2:
			return
		command = messageSplit[0].lower()
		commandArgs = messageSplit[1: 3]
		author: Chatter | PartialChatter = message.author
		authorId = author.id
		if command == "name":
			self.nameVote(authorId, messageSplit[1])
		elif self.awaitingActionInputs:
			if command in self.useNames:
				self.useVote(authorId, commandArgs)
			elif command in self.shootNames:
				self.shootVote(authorId, commandArgs)
	
	def nameVote(self, authorId: str, name: str) -> None:
		name = name[0: 5].upper()

		if authorId in self.nameVotesByUser:
			previousVote = self.nameVotesByUser[authorId]
			self.nameVotesByName[previousVote] -= 1
		
		self.vote(self.nameVotesByName, name)
		self.nameVotesByUser[authorId] = name
		print(f"Name Votes By User: {json.dumps(self.nameVotesByUser)}")
		print(f"Name Votes By Name: {json.dumps(self.nameVotesByName)}")
	
	def vote(self, dictToVoteOn: dict[str, int], vote: str) -> None:
		if vote in dictToVoteOn:
			dictToVoteOn[vote] += 1
		else:
			dictToVoteOn[vote] = 1
		print(f"Action Votes By User: {json.dumps(self.actionVotesByUser)}")
		print(f"Action Votes By Action: {json.dumps(self.actionVotesByAction)}")

	def removeExistingVote(self, authorId: str) -> None:
		if authorId in self.actionVotesByUser:
			oldVote: str = self.actionVotesByUser[authorId]
			self.actionVotesByAction[oldVote] -= 1

	def addActionVote(self, authorId: str, vote: str) -> None:
		self.actionVotesByUser[authorId] = vote
		self.vote(self.actionVotesByAction, vote)

	def shootVote(self, authorId: str, args: list[str]) -> None:
		normalizedShootVote: str | None = self.normalizeShootVote(args)
		if normalizedShootVote is None:
			return
		self.removeExistingVote(authorId)
		self.addActionVote(authorId, normalizedShootVote)
		
	def useVote(self, authorId: str, args: list[str]) -> None:
		normalizedUseVote: str | None = self.normalizeUseVote(args)
		if normalizedUseVote is None:
			return
		self.removeExistingVote(authorId)
		self.addActionVote(authorId, normalizedUseVote)

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
		

if __name__ == '__main__':
	bot = Chatbot()
	bot.run()