from ml.dataCollection.collector import dataCollector
from backend.database.connection import connection
from backend.database.createTables import tables
from backend.database.insertPastData import insertPastData
import pandas as pd

'''
One time table creation and insertion from github repo across several seasons. This only needs to occur once as 
data from repo is historical and wont be updated. 
'''
def main():

    #establish connection to database
    db = connection()
    if db.connect():
        print("Successful connection to the database.")

    #create data collector object
    c = dataCollector()

    #initialize list of seasons
    seasons = ["2024-25", "2023-24", "2022-23", "2021-22", "2020-21"]

    tableCreator = tables(db)
    tableCreator.createTables()

    #inserting data for past seasons object
    insert = insertPastData(db)

    for season in seasons:

        #collect team data and insert into database
        df = c.teamData(season)
        insert.insertTeamsData(df, season)

        #data on player id's and corresponding names
        df = c.playerIdList(season)
        insert.insertPlayers(df, season)

        #data on all players stats for the entire season (end of season stats)
        df = c.playersStatsSeason(season)
        duplicates = df[df.duplicated(subset=['first_name', 'second_name'], keep=False)]
        if not duplicates.empty:
            print(f"Found {len(duplicates)} duplicate player entries in season {season}")
            print(duplicates[['first_name', 'second_name']])
        insert.insertEndOfSeason(df, season)

        #collect data on all players performances for each gameweek in a season
        insert.getPlayerGameweek(season)

        print(f"Successfully inserted data for season: {season}!")
        #disconnect

    db.disconnect()

    if not db.connection.is_connected():
        print("Successfully created all tables, inserted all data, and disconnected from database.")


#python -m ml.dataCollection.main
if __name__ == "__main__":
    main()