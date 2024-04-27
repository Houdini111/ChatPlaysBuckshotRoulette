# About
This bot was inspired while watching https://www.twitch.tv/Cirno_TV shortly after the full game released. They made a comment about how it would be neat to have Chat Plays Buckshot Roulette. 
I thought to myself "Yeah, that would be neat. And I should be able to do that."
Well, I definitely under-estimated the complexity of interacting with the game. I certainly could have just had chat give all inputs but I didn't want to inundate them with the tedium of all the small actions. And so this got vastly more complicated.


# Installation
## Requirements
To run this program you must have Python3 installed (which can be found at https://www.python.org/downloads/) and the following python dependencies

1. pillow (Python Image Library)
2. pyautogui
3. getpixelcolor
4. TwitchIO
5. AioHttp
6. Aynscio

You can install these dependencies after python is installed by running `install.bat`; which will also prompt you to choose which Twitch channel you want the bot to read.

The bot will require its own Twitch account and be registered as a chatbot with them. After creating your account and logging in you can register the application at 
 https://dev.twitch.tv/console/apps
Save the bot's Client ID and Secret (created on that page) inside a `secrets.json` file in the root directory of the project. Those values should have they json keys of `clientId` and `secret`.
The bot should also be given a starter access token and refresh token (also saved in `secrets.json` using the keys `accessToken` and `refreshToken`). I recommend using Twitch CLI to create these 
https://github.com/twitchdev/twitch-cli
The bot will be able to update the access and refresh tokens by itself at startup so you should only need to do this once. 

The bot requires taking pixels from the screen to understand the game state. This is not possible in exclusive fullscreen mode. The game should thus be windowed but maximized. To work properly.

## Configuration

The bot has some config values you can change in `config.json`. 
These include:
1. The channel to join (set in the installation but can be changed here)
2. The default name for the player if none are chosen
3. How long to wait for chat to vote on an action
4. The cooldown for the instructions command

## Running 
If all your requirements are met then you can simply start the bot by running `start.bat`. It will activate as soon as the game is in focus and it can see it is in the starting bathroom. Boot the game and click Start Game, it will take it from there.

# Disclaimer
This bot was designed for a 1440p screen. The overlay and pixel checking are all based on that. It should scale to other 16:9 resolutions but I have not tested any. 
Further, the game overrides the cursor position if the mouse is on the screen. You should keep the cursor off the screen, but the game focused, at all time for proper functionality. 

# How the bot runs
The "bot" is actually a combination of three programs in one. 
1. The chatbot made with TwitchIO
	- Reads the chats for votes
	- Sends messages about the voting state, including when it is open and the decisions made
2. The Overlay made with Tkinter
	- Designed to be added as a program to the stream to provide additional information including voting stats and bot status
3. The Game Runner
	- Reads the game state by checking groups of displayed pixels
	- Tracks game state as well as possible
	- Enters inputs required to get to the next player turn
	- Enters the requested input from the chatbot (and thus chat)

## The Chatbot

[TODO]

## The Overlay

[TODO]

## The Game Runner

[TODO]