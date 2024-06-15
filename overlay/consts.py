from enum import Enum

class Tags(Enum):
	ACTION_VOTE_STATIC: str = "voteStatic"
	ACTION_VOTE_STATS: str = "voteStats"
	NAME_LEADERBOARD_HEADER: str = "nameLeaderboardHeader"
	NAME_LEADERBOARD_ENTRY: str = "nameLeaderboardEntry"
	SIDEBAR_ACTION_HEADER: str = "sidebarActionHeader"
	SIDEBAR_ACTION_ENTRY: str = "sidebarActionEntry"
	SIDEBAR_ADRENALINE_HEADER: str = "sidebarAdrenalineHeader"
	SIDEBAR_ADRENALINE_ENTRY: str = "sidebarAdrenalineEntry"