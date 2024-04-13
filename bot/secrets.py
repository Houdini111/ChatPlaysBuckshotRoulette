import json
import logging
from typing import Any

from .auth import make_refresh_call

logger = logging.getLogger(__name__ + '.bot.secrets')

class Secrets():
	def __init__(self):
		global secrets
		secrets = self
		self.secretsPath = "secrets.json"
		with open(self.secretsPath, 'r') as file:
			self.secrets = json.load(file)
	
	def getAccessToken(self) -> str:
		return self.secrets["accessToken"]
	
	def getRefreshToken(self) -> str:
		return self.secrets["refreshToken"]

	def getSecret(self) -> str:
		return self.secrets["secret"]

	def getClientId(self) -> str:
		return self.secrets["clientId"]

	def save_secrets(self) -> None:
		with open(self.secretsPath, 'w') as file:
			file.write(json.dumps(self.secrets))

	async def refresh_tokens_and_save(self) -> None:
		logger.debug("Refresh_tokens_and_save called. Making refresh call.")
		response = await make_refresh_call(self.getRefreshToken(), self.getClientId(), self.getSecret())
		if response is None:
			logger.warn("Refresh call returned None")
			return
		logger.debug(F"Refresh call response: {json.dumps(response)}")
		new_access_token = response["access_token"]
		new_refresh_token = response["refresh_token"]
		self.save_secrets()
		
secrets: Secrets | None = None
def getSecrets() -> Secrets:
	global secrets
	if secrets is None:
		secrets = Secrets()
	return secrets