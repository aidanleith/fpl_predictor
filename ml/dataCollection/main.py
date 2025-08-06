from ml.dataCollection.collector import dataCollector
from backend.database.connectionPast import connection
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
    seasons = ["2024-25", "2023-24", "2022-23", "2021-22", "2020-21", "2019-20"]

    tableCreator = tables(db)
    tableCreator.createTables()

    #inserting data for past seasons object
    insert = insertPastData(db)

    for season in seasons:

        #collect team data and insert into database
        df = c.teamData(season)
        insert.insertTeamsData(df, season)

        #Checks if unique player already exists, if not inserts into players table and returns unique id. Also creates seasonal mappings
        df = c.playersStatsSeason(season) #To retrieve DOB, position, and team id
        dfNames = c.playerIdList(season) #to retrieve names and seasonal id
        df_stats_clean = df.drop(columns=['first_name', 'second_name'], errors='ignore')
        merged_df = pd.merge(dfNames, df_stats_clean, on='id', how='inner')         
        print(f"Processing {len(merged_df)} players for season {season}")
        insert.insertPlayersAndMapping(merged_df, season)

        #data on all players stats for the entire season (end of season stats)
        df = c.playersStatsSeason(season)        
        insert.insertEndOfSeason(df, season)

        '''
        Inserts gameweek specific data for each player in a season. Requires dfNames due to url encoding that is required to retrieve
        the gameweekdata, cannot use query to db for existing names as they may slightly change season to season, resulting in
        non existent url being called. (EX: seamus coleman 24-25 and 23-24)
        '''
        dfNames = c.playerIdList(season)
        insert.getPlayerGameweek(season, dfNames)

        print(f"Successfully inserted data for season: {season}!")
        #disconnect

    db.disconnect()

    if not db.connection.is_connected():
        print("Successfully created all tables, inserted all data, and disconnected from database.")


#python -m ml.dataCollection.main
if __name__ == "__main__":
    main()