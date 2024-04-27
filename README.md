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

# Implementation Details
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
Primarily, the Game Runner works by understanding the order of events (for example, after leaving the bathroom you are always on the walkway with only the option to continue forward) and checking the color of pixels to check for things that aren't a guaranteed order. 

Through most of the gameplay the order of events is seemingly random. Take shooting the dealer for example. A naive approach would say the turn is over. However:
1. If the dealer was handcuffed then the player would have another turn. 
2. But even if they were, if the dealer loses then it isn't the players turn immediately anyways.
3. If that was the final shot loaded then it's time to grab more items. 

Likewise, you might make the assumption that it will eventually be the player's turn. But if the player loses then that is not the case either. 
As such, there are several game states to be handled that could happen in a mostly random order. 

So during general gameplay the bot must attempt to figure out what, if anything, it needs to do at the moment. My solution to finding this is to check the color of groups of pixels. With a sufficient color range and spread locations it should be possible to tell every unique game state apart.

### Pixel Peeping
To facilitate these checks I implemented the `pixelPeep` module and the `Peeper` and `Peep` classes inside. 

#### Peep
The Peep class is a wrapper class around my method `valuesInRangeInArea` in the `screenColors` module. The `Peep` class keeps track of its name, the area it should check, and the values it expects from the check. It also provides an error message which can be fetched in the event of a failed check.

#### Peeper
The `Peeper` class simply contains a list of `Peeps` (or `Peepers`) and will run the check for each in turn. It provides the additional functionality of logging which `Peep` failed for easier debugging.

#### valuesInRangeInArea
This method scales the 2560x1440 pixel coordinates and size and scales it to the current display, and then uses the `getpixelcolor` library to get the pixels there. Next, it checks the values of every pixel to see if it matches. It supports both ANY and AND modes for the values (which are used in `AnyWhitePeep` and `AllBlackPeep` respectively, for example).

#### Usage
Defined in the relevant classes (mostly `GameRunner`), `Peeper`s are created with a list of `Peep`s with predefined areas to check and values ot expect. Then, when the `GameRunner` wants to check the game state it can simply ask the relevant `Peeper` if it passes the check. 

### Complications
Several complications which required additional solutions were encountered along the way. Here are a few and the solutions I implemented to attempt to resolve them.
#### Flashes of Black and White
After certain actions, like being shot or using a bad pill, the screen will full screen flash black and/or white. This can interfere with basic pixel peeping. If you only check one color then such flashes would appear to be a false positive for that game state.
The solution is to ensure every check has at least some contrast. Due to the crushed colors there are many spaces that resolve to purely black. The game board also includes white lines though they often don't show as fully white, so some margin of error is needed. Including at least one of both black and white. 
By checking both then fullscreen flashes should not trigger false positives.

#### Double Checking
Some places have breif periods where the state seems to match something that is wrong. For example, after the last shot was fired then the view will breifly match the view for when it is the player's turn before switching to present the item box. 
The fullscreen flashes can do similar things, tricking even the multiple place checks if they happen at the exact timings. With as often as these checks occur such coincidences are actually surprisingly common.
To mitigate these risks these problematic game states are made to double check when they are seen. It will run a check, and if it passes it will wait for a short period of 0.1 seconds and check again. If it passes again then it is assumed to be accurate.

#### Bathroom View Bob

#### OCR

#### Adrenaline 
(theirs and ours)