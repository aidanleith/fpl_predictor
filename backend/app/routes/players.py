from fastapi import APIRouter, HTTPException, Query
from backend.app.services.playerService import playerServices
from backend.app.models import playerModel

'''
Defines all endpoints for player related requests.
'''

router = APIRouter()
playerService = playerServices()

'''Used to search a player name. Queries for player name and will return list of all similar/matching players.'''
@router.get("/search", response_model=playerModel.playerSearchResponse)
async def playerSearch(name: str = Query(..., min_length=2, description="Player name to search for.")):

    '''Note: cant use await as services functions and db are fundamentally sync. This means that this endpoint is async,
    but as soon as it hits a db call, it must halt to wait for the response. If i have 10 threads, then all threads could be handling
    different client requests but will halt when a db call is hit. This results in more memory as we are limited by number of threads
    available. If all threads are being used, clients must wait until a thread is available. With fully async and using await,
    one thread could handle multiple different requests efficiently, meaning less storage and able to handle more requests. '''
    players = playerService.playerSearch(name)

    if not players:
        raise HTTPException(status_code=404, detail="No players found with a matching name.")
    
    return playerModel.playerSearchResponse(
        players = players,
        count = len(players),
        query = name
    )

'''Endpoint for player profile page. Retrieves basic player info and all seasons played.'''
@router.get("/profile/{id}", response_model=playerModel.playerProfile)
async def playerProfilePage(id: int):

    res = playerService.playerProfile(id)

    if not res:
        raise HTTPException(status_code=404, detail="No player profile found.")

    return res

'''Accessed from player profile page and filtered by a specific season. Retrieves end of season stats and all gameweek stats.'''
@router.get("/profile/{id}/{season}", response_model=playerModel.playerSeasonPage)
async def playerProfileSeasonPage(id: int, season: str):

    eos = playerService.playerEndOfSeason(id, season)
    gwStats = playerService.playerGameweekStats(id, season)

    if not eos or not gwStats:
        raise HTTPException(status_code=404, detail="No end of season or gameweek stats available.")
    
    return playerModel.playerSeasonPage(
        endOfSeason=eos,
        gameweekStats=gwStats
    )








