from pydantic import BaseModel
from typing import List

#individual player data returned from search
class playerSearchResult(BaseModel):
    id: int
    first_name: str
    last_name: str
    team_name: str
    position: str

#count to display on UI how many results were found, query is name of searched player so could display "results for query"
#players stores list of players returned with matching names
class playerSearchResponse(BaseModel):
    players: List[playerSearchResult]
    count: int
    query: str

class playerProfile(BaseModel):
    first_name: str
    last_name:str
    team_name: str
    position: str
    seasons: List[str] #list of seasons for which player has played
    




