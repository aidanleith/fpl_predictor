import urllib.parse
from mysql.connector import Error
from ml.dataCollection.collector import dataCollector
from ml.preprocessing.featureEngineering import featureEngineer
import pandas as pd
import math

#important cursor/connection functions: connection.commit(), cursor.execute(sql, params_list), cursor.fetchone(), 
#cursor.fetchmany(), cursor.fetchall()

class insertPastData:

    def __init__(self, dbConnection):
        self.collect = dataCollector()
        self.engineer = featureEngineer(None, None)
        self.db = dbConnection
        self.cursor = self.db.getCursor()
    
    #takes df paramater which stores data and season specifying which season, returns true if successfully inserted into table
    def insertTeamsData(self, df, season) -> bool:

        try:
            for i, row in df.iterrows():
                sql = """
                INSERT INTO teams (
                team_id, season, team_name, team_pos_final, strength, strength_overall_home, 
                strength_overall_away, strength_attack_home, strength_attack_away, 
                strength_defense_home, strength_defense_away
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                #second parameter is default value if missing from df, prevents crashing
                values = (
                    row.get('id', -1),
                    season,
                    row.get('name', ''),
                    row.get('team_pos_final', -1),
                    row.get('strength', -1),
                    row.get('strength_overall_home', -1),
                    row.get('strength_overall_away', -1),
                    row.get('strength_attack_home', -1),
                    row.get('strength_attack_away', -1),
                    row.get('strength_defense_home', -1),
                    row.get('strength_defense_away', -1)
                )

                self.cursor.execute(sql, values)

            self.db.commit()
            print(f"Inserted teams data for season {season} successfully.")
            return True     
           
        except Error as e:
            print(f'Error occurred inserting teams data for season {season} : {e}')
            return False
    
    #insert specifically to players table. returns player unique id
    def insertPlayers(self, first_name, last_name, dob):
        """Simple: check if player exists, if not insert them, return ID"""
        try:
            # Handle NaN DOB
            if isinstance(dob, float) and math.isnan(dob):
                dob = None
            
            # Check if player exists (ignore duplicates with same name/DOB)
            check_sql = "SELECT id FROM players WHERE first_name = %s AND last_name = %s LIMIT 1"
            self.cursor.execute(check_sql, (first_name, last_name))
            result = self.cursor.fetchone()
            
            if result:
                return result[0]  # Return existing player ID
            
            # Insert new player
            insert_sql = "INSERT INTO players (first_name, last_name, DOB) VALUES (%s, %s, %s)"
            self.cursor.execute(insert_sql, (first_name, last_name, dob))
            return self.cursor.lastrowid
                
        except Error as e:
            print(f"Error with player {first_name} {last_name}: {e}")
            return None

        
    #insert players table and season mappings
    def insertPlayersAndMapping(self, merged_df, season):
        """Simple: merge dataframes, get/create player ID, insert mapping"""
        try:
            
            processed = 0
            skipped = 0
            
            for _, row in merged_df.iterrows():
                fpl_id = row.get('id', -1)
                first_name = row.get('first_name', '').strip()
                last_name = row.get('second_name', '').strip()  # Use second_name as last_name
                dob = row.get('birth_date', None)
                positionId = row.get('element_type', -1)
                if positionId == 1:
                    position = "GK"
                elif positionId == 2:
                    position = "DEF"
                elif positionId == 3:
                    position = "MID"
                elif positionId == 4:
                    position = "FWD"
                elif positionId == 5:
                    position = "Manager"
                team_id = row.get('team', -1)
                
                # Skip if missing essential data
                if not first_name or not last_name or fpl_id == -1 or team_id == -1:
                    skipped += 1
                    continue
                
                # Check if mapping already exists, handles ben davies case
                check_mapping = "SELECT 1 FROM playerSeasonMapping WHERE fpl_season_id = %s AND season = %s"
                self.cursor.execute(check_mapping, (fpl_id, season))
                if self.cursor.fetchone():
                    continue  # Skip if mapping exists
                
                # Get or create player
                player_id = self.insertPlayers(first_name, last_name, dob)
                if not player_id:
                    skipped += 1
                    continue
                
                # Insert mapping
                mapping_sql = """
                INSERT INTO playerSeasonMapping (player_id, season, fpl_season_id, position, team_id)
                VALUES (%s, %s, %s, %s, %s)
                """
                
                try:
                    self.cursor.execute(mapping_sql, (player_id, season, fpl_id, position, team_id))
                    processed += 1
                except Error as e:
                    print(f"Error inserting {first_name} {last_name}: {e}")
                    skipped += 1
            
            self.db.commit()
            print(f"Processed {processed} players, skipped {skipped}")
            return True
            
        except Exception as e:
            print(f"Error in insertPlayersAndMapping: {e}")
            self.db.rollback()
            return False
    def insertEndOfSeason(self, df, season) -> bool:
        '''
        This function is used for specific columns in the df that have potentially float64 values and float64 nan values.
        Since nan is a numpy value, it is not recognized as null by mysql, so I convert the value to None which is recognized
        as NULL by mysql. 
        '''
        def safe_value(val):
            if isinstance(val, float) and math.isnan(val):
                return None
            return val
        
        try:
            
            for i, row in df.iterrows():

                seasonId = row.get('id', -1)

                query = """
                SELECT player_id
                FROM playerSeasonMapping
                WHERE season = %s AND fpl_season_id = %s
                """
                self.cursor.execute(query, (season, seasonId))
                res = self.cursor.fetchone()

                 #handle case where no player found
                if res is None:
                    print(f"No player found for FPL ID {seasonId} in season {season}")
                    continue
                    
                uniqueId = res[0] 
                
                #requires ignore due to earlier seasons having duplicated player files. hence, when it reads in the first file,
                #it retrieves id for that name. then it reads the second file, retrieves the same id from the players table, and 
                #returns duplicated primary key error. UPDATE: no longer an issue, using uniquely generated id keys
                sql = """
                INSERT IGNORE INTO endOfSeason
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s
                )
                """

                #check for -1 values, empty names, or NaN values in freekicks order
                values = (
                    uniqueId,
                    season,
                    row.get('total_points', -50),
                    row.get('goals_scored', -1),
                    row.get('assists', -1),
                    row.get('minutes', -1),
                    row.get('own_goals', -1),
                    row.get('penalties_missed', -1),
                    safe_value(row.get('penalties_order', -1)),
                    row.get('penalties_saved', -1),
                    row.get('points_per_game', -1),
                    row.get('points_per_game_rank', -1),
                    row.get('expected_assists', -1),
                    row.get('expected_assists_per_90', -1),
                    row.get('expected_goal_involvements', -1),
                    row.get('expected_goal_involvements_per_90', -1),
                    row.get('expected_goals', -1),
                    row.get('expected_goals_per_90', -1),
                    row.get('expected_goals_conceded', -1),
                    row.get('expected_goals_conceded_per_90', -1),
                    row.get('clean_sheets', -1),
                    row.get('clean_sheets_per_90', -1),
                    safe_value(row.get('corners_and_indirect_freekicks_order', -1)),
                    safe_value(row.get('direct_freekicks_order', -1)),
                    row.get('dreamteam_count', -1),
                    row.get('goals_conceded', -1),
                    row.get('goals_conceded_per_90', -1),
                    row.get('yellow_cards', -1),
                    row.get('red_cards', -1),
                    row.get('bonus', -1),
                    row.get('bps', -1),
                    row.get('saves', -1),
                    row.get('saves_per_90', -1),
                    row.get('influence', -1),
                    row.get('creativity', -1),
                    row.get('creativity_rank', -1),
                    row.get('threat', -1),
                    row.get('ict_index', -1),
                    row.get('cost', -1),
                    row.get('selected_by_percent', -1),
                    row.get('selected_rank', -1),
                    row.get('starts', -1),
                    row.get('starts_per_90', -1),
                    row.get('transfers_in', -1),
                    row.get('transfers_out', -1)
                )

                self.cursor.execute(sql, values)

            self.db.commit()
            print(f"Successfully added end of season stats for all players in season: {season}.")
            return True
        
        except Error as e:
            print(f"Error occurred inserting data to end of season stats: {e}")
            return False
        
    def insertGameweekData(self, df, season) -> bool:
        #note: INSERT IGNORE required as human error caused some duplicate gameweek numbers in github repo.
        #Since there is a composite primary key of season, gameweek, and id, when it tries to insert for the same player
        #in the same season with a FALSELY same gw, there will be an error.
        #As a result, there will be around a 3-5% loss on data for some players in a season. 
        #UPDATE ON note ABOVE: created way to retrieve directly from gw merged file and fix repeating gw's in data collector file
        #and feature engineering file
        try:

            for i, row in df.iterrows():

                seasonId = row.get('element', -1)

                query = """
                SELECT player_id
                FROM playerSeasonMapping
                WHERE season = %s AND fpl_season_id = %s
                """
                self.cursor.execute(query, (season, seasonId))
                res = self.cursor.fetchone()

                 #handle case where no player found
                if res is None:
                    print(f"No player found for FPL ID {seasonId} in season {season}")
                    continue
                    
                uniqueId = res[0] 

                sql = """
                INSERT IGNORE INTO gameweekStats 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                values = (
                    uniqueId,
                    season,
                    row.get('GW', -1),
                    row.get('opponent_team', -50),
                    row.get('was_home', -1),
                    row.get('total_points', -1),
                    row.get('expected_assists', -1),
                    row.get('expected_goal_involvements', -1),
                    row.get('expected_goals', -1),
                    row.get('expected_goals_conceded', -1),
                    row.get('starts', -1),
                    row.get('transfers_in', -1),
                    row.get('transfers_out', -1),
                    row.get('minutes', -1),
                    row.get('goals_scored', -1),
                    row.get('assists', -1),
                    row.get('clean_sheets', -1),
                    row.get('goals_conceded', -1),
                    row.get('own_goals', -50),
                    row.get('penalties_saved', -1),
                    row.get('penalties_missed', -1),
                    row.get('yellow_cards', -1),
                    row.get('red_cards', -1),
                    row.get('saves', -1),
                    row.get('bonus', -1),
                    row.get('bps', -1),
                    row.get('influence', -1),
                    row.get('creativity', -1),
                    row.get('threat', -1),
                    row.get('ict_index', -1),
                    row.get('value', -1),
                    row.get('selected', -1),
                    row.get('team_a_score', -1),
                    row.get('team_h_score', -1)
                )

                self.cursor.execute(sql, values)

            self.db.commit()
            return True
        
        except Error as e:
            print(f"Error occurred inserting gameweek data for season: {season}, player: {id}, error: {e}")
            return False
        
    #needed if u want to collect data for all gameweeks on specific player as it creates encoded part need for url with gameweek and names
    def getPlayerGameweek(self, season, dfNames):

        try:
            sql = "SELECT fpl_season_id, player_id FROM playerSeasonMapping WHERE season = %s"
            #pass season through as tuple (required)
            self.cursor.execute(sql, (season,))
            players = self.cursor.fetchall()
            inserted = 0

            #required to retrieve the name as stored for this season to get the url, may change season to season
            for fpl_season_id, player_id in players:
                season_name_row = dfNames[dfNames['id'] == fpl_season_id]
                if not season_name_row.empty:
                    firstName = season_name_row.iloc[0]['first_name']
                    lastName = season_name_row.iloc[0]['second_name']

                #players with spaces in names must be encoded to not have url error
                encoded_first_name = urllib.parse.quote(firstName)
                encoded_last_name = urllib.parse.quote(lastName)
                urlNameAndId = f"{encoded_first_name}_{encoded_last_name}_{fpl_season_id}"
                
                df = self.collect.playerPerformanceGameweek(season, urlNameAndId)

                #now fix repeating gw error
                df = self.engineer.fixGwRepeats(df)

                try:
                    if self.insertGameweekData(df, season):
                        inserted += 1
                    else:
                        print(f"Inserted so far: {inserted}. Problem with {firstName} {lastName}")

                except Error as e:
                    print(f"Failed inserting player {firstName} {lastName} with error: {e}")

        except Error as e:
            print(f"Failed to either collect df or retrieve players from database with error: {e}")
            return False
        
        print(f"Added {inserted} number of players for season: {season}")




        



