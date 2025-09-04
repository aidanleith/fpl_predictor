from pydantic import BaseModel
from typing import List, Optional

'''individual player data returned from search'''
class playerSearchResult(BaseModel):
    id: int
    first_name: str
    last_name: str
    dob: str
    team_name: str
    team_id: int
    position: str
    latestSeason: str


'''count to display on UI how many results were found, query is name of searched player so could display "results for query"
players stores list of players returned with matching names'''
class playerSearchResponse(BaseModel):
    players: List[playerSearchResult]
    count: int
    query: str

'''model for player profile page'''
class playerProfile(BaseModel):
    first_name: str
    last_name: str
    dob: str
    current_team: str
    curr_position: str
    all_seasons: List[str]

'''Individual players end of season stats, also contains basic player info.'''
#had to add optional as server was returning 500 error code due to dob and order being null, however originally were required types (ex:john egan)
class playerEndOfSeason(BaseModel):
    first_name: str
    last_name: str
    dob: Optional[str] = None
    season: str
    fpl_season_id: int
    position: str
    team_name: str
    total_points: int
    goals_scored: int
    assists: int
    minutes: int
    own_goals: int
    penalties_missed: int
    penalties_order: Optional[float] = None
    penalties_saved: int
    points_per_game: float
    points_per_game_rank: int
    expected_assists: float
    expected_assists_per_90: float
    expected_goal_involvements: float
    expected_goal_involvements_per_90: float
    expected_goals: float
    expected_goals_per_90:float
    expected_goals_conceded: float
    expected_goals_conceded_per_90: float
    yellow_cards: int
    red_cards: int
    bonus: int
    bps: int
    saves: int
    saves_per_90: float
    influence:float
    creativity: float
    creativity_rank: int
    threat: float
    ict_index: float
    cost: float
    selected_by_percent: float
    selected_rank: int
    starts: int
    starts_per_90: float
    transfers_in: int
    transfers_out: int

'''Stores gameweek stats for a season'''
class playerGameweekStats(BaseModel):
    player_id: int
    season: str
    gameweek: int
    opponent_team: int
    opponent_name: str
    was_home: int
    round_points: int
    expected_assists: float
    expected_goal_involvements: float
    expected_goals:float
    expected_goals_conceded:float
    starts:int
    transfers_in:int
    transfers_out:int
    minutes:int
    goals_scored:int
    assists:int
    clean_sheets:int
    goals_conceded:int
    own_goals:int
    penalties_saved:int
    penalties_missed:int
    yellow_cards:int
    red_cards:int
    saves:int
    bonus:int
    bps:int
    influence:float
    creativity: float
    threat:float
    ict_index:float
    value:float
    selected:int
    team_away_score:int
    team_home_score:int


'''Contains a players end of seasons stats and list of gameweek stats for a season'''
class playerSeasonPage(BaseModel):
    endOfSeason: playerEndOfSeason
    gameweekStats: List[playerGameweekStats]


    




