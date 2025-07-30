from mysql.connector import Error

'''
One time creation of all tables needed in database.
'''
class tables:

    def __init__(self, dbConnection):
        self.db = dbConnection
     
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
                first_name VARCHAR(100),
                second_name VARCHAR (100),
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

            pointPredictions = """
            CREATE TABLE IF NOT EXISTS pointPredictions(
                player_id INT,
                gameweek INT,
                points DECIMAL(10,2),
                PRIMARY KEY (player_id),
                FOREIGN KEY (player_id) REFERENCES players(id)
            )
            """

            self.cursor = self.db.getCursor()

            #execute commands and commit to database
            self.cursor.execute(players)
            self.cursor.execute(teamSql)
            self.cursor.execute(endOfSeason)
            self.cursor.execute(gameweekData)
            self.cursor.execute(pointPredictions)
            self.db.commit()
            print("Successfully created tables.")
            return True

        except Error as e:
            print(f"Error occurred creating tables: {e}")
            return False