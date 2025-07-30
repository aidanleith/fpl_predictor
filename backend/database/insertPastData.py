import urllib.parse
from mysql.connector import Error
from ml.dataCollection.collector import dataCollector
from ml.preprocessing.featureEngineering import featureEngineer

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
        
    def insertPlayers(self, df, season) -> bool:
        try:
            for i, row in df.iterrows():

                sql = """
                INSERT INTO players (id, season, first_name, last_name)
                VALUES (%s, %s, %s, %s)
                """

                #if id is -1, there was no id provided. check for this
                values = (
                    row.get('id', -1),
                    season,
                    row.get('first_name', ''),
                    row.get('second_name', '')
                )

                self.cursor.execute(sql, values)

            self.db.commit()
            print(f"Players successfully added for season: {season}")
            return True
        
        except Error as e:
            print(f"Error occurred inserting to player table: {e}")
            return False

    def insertEndOfSeason(self, df, season) -> bool:
        try:
            
            for i, row in df.iterrows():

                query = "SELECT id FROM players WHERE first_name = %s AND last_name = %s AND season = %s"
                self.cursor.execute(query, (row.get('first_name', ''), row.get('second_name', ''), season))
                res = self.cursor.fetchone()

                #avoids unread result found error in cursor due to not consuming all results
                #caused by duplicate player files returning several results, adding unused to buffer
                while self.cursor.nextset(): 
                    pass

                if res is None:
                    print(f"Error finding {row.get('first_name', '')} {row.get('second_name', '')} id")
                    continue

                #returns tuple so need to get first item despite there only being one item
                id = res[0]
                
                #requires ignore due to earlier seasons having duplicated player files. hence, when it reads in the first file,
                #it retrieves id for that name. then it reads the second file, retrieves the same id from the players table, and 
                #returns duplicated primary key error.
                sql = """
                INSERT IGNORE INTO endOfSeason (
                player_id, first_name, second_name, position, season, total_points, goals_scored, assists, clean_sheets,
                goals_conceded, yellow_cards, red_cards, bonus, bps, influence, creativity, 
                threat, ict_index, cost, selected_by_percent
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                #check for - values or empty names 
                values = (
                    id,
                    row.get('first_name', ''),
                    row.get('second_name', ''),
                    row.get('element_type', ''),
                    season,
                    row.get('total_points', -50),
                    row.get('goals_scored', -1),
                    row.get('assists', -1),
                    row.get('clean_sheets', -1),
                    row.get('goals_conceded', -1),
                    row.get('yellow_cards', -1),
                    row.get('red_cards', -1),
                    row.get('bonus', -1),
                    row.get('bps', -1),
                    row.get('influence', -1),
                    row.get('creativity', -1),
                    row.get('threat', -1),
                    row.get('ict_index', -1),
                    row.get('cost', -1),
                    row.get('selected_by_percent', -1)
                )

                self.cursor.execute(sql, values)

            self.db.commit()
            print(f"Successfully added end of season stats for all players in season: {season}.")
            return True
        
        except Error as e:
            print(f"Error occurred inserting data to end of season stats: {e}")
            return False
        
    def insertGameweekData(self, df, season, id, firstName, secondName) -> bool:
        #note: INSERT IGNORE required as human error caused some duplicate gameweek numbers in github repo.
        #Since there is a composite primary key of season, gameweek, and id, when it tries to insert for the same player
        #in the same season with a FALSELY same gw, there will be an error.
        #As a result, there will be around a 3-5% loss on data for some players in a season. 
        #UPDATE ON note ABOVE: created way to retrieve directly from gw merged file and fix repeating gw's in data collector file
        #and feature engineering file
        try:
            for i, row in df.iterrows():
                sql = """
                INSERT INTO gameweekStats (
                    player_id, first_name, second_name, season, gameweek, opponent_team, was_home, round_points, expected_assists,
                    expected_goal_involvements, expected_goals, expected_goals_conceded, starts, transfers_in, 
                    transfers_out, minutes, goals_scored, assists, clean_sheets, goals_conceded, own_goals,
                    penalties_saved, penalties_missed, yellow_cards, red_cards, saves, bonus, bps, 
                    influence, creativity, threat, ict_index, value, selected
                ) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                         %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                values = (
                    id,
                    firstName,
                    secondName,
                    season,
                    row.get('GW', -1),
                    row.get('opponent_team', -50),
                    row.get('was_home', -1),
                    row.get('round_points', -1),
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
                    row.get('selected', -1)
                )

                self.cursor.execute(sql, values)

            self.db.commit()
            return True
        
        except Error as e:
            print(f"Error occurred inserting gameweek data for season: {season}, player: {id}, error: {e}")
            return False
        
    #needed if u want to collect data for all gameweeks on specific player as it creates encoded part need for url with gameweek and names
    def getPlayerGameweek(self, season):

        try:
            sql = "SELECT id, first_name, last_name FROM players WHERE season = %s"
            #pass season through as tuple (required)
            self.cursor.execute(sql, (season,))
            players = self.cursor.fetchall()
            inserted = 0

            for id, firstName, lastName in players:

                #players with spaces in names must be encoded to not have url error
                encoded_first_name = urllib.parse.quote(firstName)
                encoded_last_name = urllib.parse.quote(lastName)
                urlNameAndId = f"{encoded_first_name}_{encoded_last_name}_{id}"
                
                df = self.collect.playerPerformanceGameweek(season, urlNameAndId)

                #now fix repeating gw error
                df = self.engineer.fixGwRepeats(df)

                try:
                    if self.insertGameweekData(df, season, id, firstName, lastName):
                        inserted += 1
                    else:
                        print(f"Inserted so far: {inserted}. Problem with {firstName} {lastName}")

                except Error as e:
                    print(f"Failed inserting player {firstName} {lastName} with error: {e}")

        except Error as e:
            print(f"Failed to either collect df or retrieve players from database with error: {e}")
            return False
        
        print(f"Added {inserted} number of players for season: {season}")




        



