from ml.dataCollection.collector import dataCollector
from backend.database import databaseManager
import pandas as pd

def main():

    db = databaseManager()
    db.connect()
    c = dataCollector()
    season = "2024-25"

    db.createTables()

    #collect team data and insert into database
    df = c.teamData(season)
    db.insertTeamsData(df, season)

    #data on player id's and corresponding names
    df = c.playerIdList(season)
    db.insertPlayers(df, season)

    #data on all players stats for the entire season (end of season stats)
    df = c.playersStatsSeason(season)
    db.insertEndOfSeason(df, season)

    #collect data on all players performances for each gameweek in a season
    db.getPlayerGameweek(season)

    #disconnect
    db.disconnect()


#python -m ml.dataCollection.main
if __name__ == "__main__":
    main()