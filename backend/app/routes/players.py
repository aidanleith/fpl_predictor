from fastapi import APIRouter, HTTPException, Query
from backend.app.services.playerService import playerServices
from backend.app.models import playerModel

'''
Defines all endpoints for player related requests.
'''

router = APIRouter()
playerService = playerServices()

#implement tags and response model
@router.get("/search", response_model=playerModel.PlayerSearchResponse)
async def playerSearch(name: str = Query(..., min_length=2, description="Player name to search for.")):

    players = await playerService.playerSearch(name)

    if not players:
        raise HTTPException(status_code=404, detail="No players found with a matching name.")
    

    return playerModel.PlayerSearchResponse(
        players = players,
        count = len(players),
        query = name
    )

@router.get("/profile/{id}", response_model=playerModel.playerProfile)
async def playerProfilePage(id: int):

    res = await playerService.playerProfile(id)

    if not res:
        raise HTTPException(status_code=404, detail="No player profile found.")

    return playerModel.playerProfile(

    )





