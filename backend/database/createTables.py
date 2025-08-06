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
                id INT AUTO_INCREMENT PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                DOB VARCHAR(50)
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

            playerSeasonMapping = """
            CREATE TABLE IF NOT EXISTS playerSeasonMapping (
                    player_id INT,
                    season VARCHAR(20),
                    fpl_season_id INT,
                    position VARCHAR(20),
                    team_id INT,
                    PRIMARY KEY (player_id, season),
                    FOREIGN KEY (player_id) REFERENCES players(id),
                    FOREIGN KEY (team_id, season) REFERENCES teams(team_id, season)
                )
            """

            #create table for storing individual player data for a season
            endOfSeason = """
            CREATE TABLE IF NOT EXISTS endOfSeason (
                player_id INT,
                season VARCHAR(20),
                total_points INT,
                goals_scored INT,
                assists INT,
                minutes INT,
                own_goals INT,
                penalties_missed INT,
                penalties_order FLOAT NULL,
                penalties_saved INT,
                points_per_game DECIMAL(10,2),
                points_per_game_rank INT,
                expected_assists DECIMAL(10,2),
                expected_assists_per_90 DECIMAL(10,2),
                expected_goal_involvements DECIMAL(10,2),
                expected_goal_involvements_per_90 DECIMAL(10,2),
                expected_goals DECIMAL(10,2),
                expected_goals_per_90 DECIMAL(10,2),
                expected_goals_conceded DECIMAL(10,2),
                expected_goals_conceded_per_90 DECIMAL(10,2),
                clean_sheets INT,
                clean_sheets_per_90 DECIMAL(10,2),
                corners_and_indirect_freekicks_order FLOAT NULL,
                direct_freekicks_order FLOAT NULL,
                dreamteam_count INT,
                goals_conceded INT,
                goals_conceded_per_90 DECIMAL(10,2),
                yellow_cards INT,
                red_cards INT,
                bonus INT,
                bps INT,
                saves INT,
                saves_per_90 DECIMAL(10,2),
                influence DECIMAL(10,2),
                creativity DECIMAL(10,2),
                creativity_rank INT,
                threat DECIMAL(10,2),
                ict_index DECIMAL(10,2),
                cost DECIMAL(10,2),
                selected_by_percent DECIMAL(10,2),
                selected_rank INT,
                starts INT,
                starts_per_90 DECIMAL(10,2),
                transfers_in INT,
                transfers_out INT,
                PRIMARY KEY (player_id, season),
                FOREIGN KEY (player_id, season) REFERENCES playerSeasonMapping(player_id, season)
            )
            """

            #this table stores every players stats for all gameweeks
            gameweekData = """
            CREATE TABLE IF NOT EXISTS gameweekStats (
                player_id INT,
                season VARCHAR(20),
                gameweek INT,
                opponent_team INT,
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
                team_away_score INT,
                team_home_score INT,
                PRIMARY KEY (player_id, gameweek, season),
                FOREIGN KEY (player_id, season) REFERENCES playerSeasonMapping(player_id, season),
                FOREIGN KEY (opponent_team, season) REFERENCES teams(team_id, season)
            )
            """

            pointPredictions = """
            CREATE TABLE IF NOT EXISTS pointPredictions(
                player_id INT,
                gameweek INT,
                season VARCHAR(20),
                points DECIMAL(10,2),
                PRIMARY KEY (player_id, gameweek, season),
                FOREIGN KEY (player_id, season) REFERENCES playerSeasonMapping(player_id, season)
            )
            """

            self.cursor = self.db.getCursor()

            #execute commands and commit to database
            self.cursor.execute(players)
            self.cursor.execute(teamSql)
            self.cursor.execute(playerSeasonMapping)
            self.cursor.execute(endOfSeason)
            self.cursor.execute(gameweekData)
            self.cursor.execute(pointPredictions)
            self.db.commit()
            print("Successfully created tables.")
            return True

        except Error as e:
            print(f"Error occurred creating tables: {e}")
            return False