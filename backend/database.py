import urllib.parse
from ml.dataCollection.config import databaseConfig
import mysql.connector
from mysql.connector import Error
from ml.dataCollection.collector import dataCollector

#important cursor/connection functions: connection.commit(), cursor.execute(sql, params_list), cursor.fetchone(), 
#cursor.fetchmany(), cursor.fetchall()

class databaseManager:

    def __init__(self):
        self.config = databaseConfig()
        self.collect = dataCollector()
        self.connection = None
        self.cursor = None
    
    def connect(self) -> bool:
        try:
            self.connection = mysql.connector.connect(
                user = self.config.username,
                password = self.config.password,
                database = self.config.database,
                host = self.config.host,
                port = self.config.port
            )

            if self.connection.is_connected():
                self.cursor = self.connection.cursor()
            return True

        except Error as e:
            return False
        
    def disconnect(self) -> bool:
        try:
            if self.cursor is not None:
                self.cursor.close()
            if self.connection is not None and self.connection.is_connected:
                self.connection.close()
            return True
        
        except Error as e:
            return False
        
    def createTables(self) -> bool:
        try:

            players = """
            CREATE TABLE IF NOT EXISTS players (
                id INT,
                season VARCHAR(20),
                first_name VARCHAR(50),
                last_name VARCHAR(50),
                PRIMARY KEY (id, season)
            )
            """

            #create table for storing team data at the end of a season
            teamSql = """
            CREATE TABLE IF NOT EXISTS teams (
                team_id INT,
                season VARCHAR(20),
                team_name VARCHAR(50),
                team_pos_final INT,
                strength INT,
                strength_overall_home INT,
                strength_overall_away INT,
                strength_attack_home INT,
                strength_attack_away INT,
                strength_defense_home INT,
                strength_defense_away INT,
                PRIMARY KEY (team_id, season)
            )
            """

            #create table for storing individual player data for a season
            endOfSeason = """
            CREATE TABLE IF NOT EXISTS endOfSeason (
                player_id INT,
                first_name VARCHAR(100) NOT NULL,
                second_name VARCHAR(100) NOT NULL,
                position VARCHAR(10),
                season VARCHAR(20),
                total_points INT,
                goals_scored INT,
                assists INT,
                clean_sheets INT,
                goals_conceded INT,
                yellow_cards INT,
                red_cards INT,
                bonus INT,
                bps INT,
                influence DECIMAL(10,2),
                creativity DECIMAL(10,2),
                threat DECIMAL(10,2),
                ict_index DECIMAL(10,2),
                cost DECIMAL(10,2),
                selected_by_percent DECIMAL(10,2),
                PRIMARY KEY (player_id, season),
                FOREIGN KEY (player_id, season) REFERENCES players(id, season)
            )
            """

            #this table stores every players stats for all gameweeks
            gameweekData = """
            CREATE TABLE IF NOT EXISTS gameweekStats (
                player_id INT,
                season VARCHAR(20),
                gameweek INT,
                opponent_team VARCHAR(50),
                was_home BOOLEAN,
                round_points INT,
                expected_assists DECIMAL(10,2),
                expected_goal_involvements DECIMAL(10,2),
                expected_goals DECIMAL(10,2),
                expected_goals_conceded DECIMAL(10,2),
                starts INT,
                transfers_in INT,
                transfers_out INT,
                minutes INT,
                goals_scored INT,
                assists INT,
                clean_sheets INT,
                goals_conceded INT,
                own_goals INT,
                penalties_saved INT,
                penalties_missed INT,
                yellow_cards INT,
                red_cards INT,
                saves INT,
                bonus INT,
                bps INT,
                influence DECIMAL(10,2),
                creativity DECIMAL(10,2),
                threat DECIMAL(10,2),
                ict_index DECIMAL(10,2),
                value DECIMAL(10,2),
                selected INT,
                PRIMARY KEY (player_id, gameweek, season),
                FOREIGN KEY (player_id, season) REFERENCES players(id, season)
            )
            """

            #execute commands and commit to database
            self.cursor.execute(players)
            self.cursor.execute(teamSql)
            self.cursor.execute(endOfSeason)
            self.cursor.execute(gameweekData)
            self.connection.commit()
            print("Successfully created tables.")
            return True

        except Error as e:
            print(f"Error occurred creating tables: {e}")
            return False
    
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

            self.connection.commit()
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

            self.connection.commit()
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

                if res is None:
                    print(f"Error finding {row.get('first_name', '')} {row.get('second_name', '')} id")
                    continue

                #returns tuple so need to get first item despite there only being one item
                id = res[0]
                
                sql = """
                INSERT INTO endOfSeason (
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
                #use tuple as opposed to a list because they are immutable

            self.connection.commit()
            print(f"Successfully added end of season stats for all players in season: {season}.")
            return True
        
        except Error as e:
            print(f"Error occurred inserting data to end of season stats: {e}")
            return False
        
    def insertGameweekData(self, df, season, id) -> bool:
        #note: INSERT IGNORE required as human error caused some duplicate gameweek numbers in github repo.
        #Since there is a composite primary key of season, gameweek, and id, when it tries to insert for the same player
        #in the same season with a FALSELY same key, there will be an error.
        #As a result, there will be around a 3-5% loss on data for some players in a season. 
        try:
            for i, row in df.iterrows():
                sql = """
                INSERT IGNORE INTO gameweekStats (
                    player_id, season, gameweek, opponent_team, was_home, round_points, expected_assists,
                    expected_goal_involvements, expected_goals, expected_goals_conceded, starts, transfers_in, 
                    transfers_out, minutes, goals_scored, assists, clean_sheets, goals_conceded, own_goals,
                    penalties_saved, penalties_missed, yellow_cards, red_cards, saves, bonus, bps, 
                    influence, creativity, threat, ict_index, value, selected
                ) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                         %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                values = (
                    id,
                    season,
                    row.get('round', -1),
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
            
            self.connection.commit()
            print("Gameweek data successfully added!")
            return True
        
        except Error as e:
            print(f"Error occurred inserting gameweek data for season: {season}, player: {id}, error: {e}")
            return False
        
    def getPlayerGameweek(self, season):

        try:
            sql = "SELECT id, first_name, last_name FROM players WHERE season = %s"
            #pass season through as tuple (required)
            self.cursor.execute(sql, (season,))
            players = self.cursor.fetchall()
            inserted = 0

            for id, first_name, last_name in players:

                #players with spaces in names must be encoded to not have url error
                encoded_first_name = urllib.parse.quote(first_name)
                encoded_last_name = urllib.parse.quote(last_name)
                urlNameAndId = f"{encoded_first_name}_{encoded_last_name}_{id}"
                
                df = self.collect.playerPerformanceGameweek(season, urlNameAndId)

                try:
                    if self.insertGameweekData(df, season, id):
                        inserted += 1
                        print(f"Player: {first_name} {last_name} was added.")
                    else:
                        print(f"Inserted so far: {inserted}. Problem with {first_name} {last_name}")

                except Error as e:
                    print(f"Failed inserting player {first_name} {last_name} with error: {e}")

        except Error as e:
            print(f"Failed to either collect df or retrieve players from database with error: {e}")
            return False
        
        print(f"Added {inserted} number of players for season: {season}")




        



