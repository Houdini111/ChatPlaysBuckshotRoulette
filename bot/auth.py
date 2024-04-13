from typing import Any
import aiohttp
import logging

logger = logging.getLogger(__name__ + '.bot.auth')

async def make_refresh_call(refresh_token: str, client_id: str, client_secret: str) -> dict[str, Any] | None:
    logger.debug("make_refresh_call called")
    url = "https://id.twitch.tv/oauth2/token"
    form_data = form_data = "grant_type=refresh_token&refresh_token="+refresh_token+"&client_id="+client_id+"&client_secret="+client_secret+"&grant_type=refresh_token'"
    headers = {"content-type":"application/x-www-form-urlencoded"}
    logger.debug("Data prepared for refresh call, starting http session")
    async with aiohttp.ClientSession() as session:
        logger.debug("Refresh call session opened. Making call.")
        async with session.post(url, data=form_data, headers=headers, timeout=60) as response:
            logging.debug("Refresh call made. Attempting to get response body.")
            try:
                body = await response.json()
            except Exception as e:
                logger.exception("Failed to get response. ", e)
                return None
            logger.info(f"Completed twitch refresh call. Response code: {response.status}")
            if response.status == 200:
                return body
            else:
                logger.error(f"Bad response. RESEPONSE: [[{response}]] BODY: [[{body}]]")
                return None