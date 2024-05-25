from enum import Enum

class Tags(Enum):
	ACTION_VOTE_STATIC: str = "voteStatic"
	ACTION_VOTE_STATS: str = "voteStats"
	NAME_LEADERBOARD: str = "nameLeaderboard"
	NAME_LEADERBOARD_HEADER: str = "nameLeaderboardHeader"
	NAME_LEADERBOARD_ENTRY: str = "nameLeaderboardEntry"