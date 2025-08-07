from backend.database.connection import connection
from backend.app.models import playerModel

class playerServices():

    def __init__(self):
        self.db = connection()

    '''searches for all players with similar names and returns id, names, DOB, team id/name, latest season, and position'''
    def playerSearch(self, name):

        search = f"%{name.lower()}%"
        query = """
        SELECT DISTINCT p.id, p.first_name, p.last_name, p.DOB, psm.team_id, psm.position, psm.season, t.team_name
        FROM players p
        INNER JOIN playerSeasonMapping psm ON p.id = psm.player_id
        INNER JOIN teams t ON psm.team_id = t.team_id AND psm.season = t.season
        WHERE (LOWER(p.first_name) LIKE %s 
            OR LOWER(p.last_name) LIKE %s 
            OR LOWER(CONCAT(p.first_name, ' ', p.last_name)) LIKE %s)
            AND psm.season = (SELECT MAX(season) FROM playerSeasonMapping WHERE player_id = p.id)
        ORDER BY p.last_name, p.first_name
        """

        res = self.db.execute_query(query, (search, search, search), fetch_results=True)

        players = []
        for row in res:
            player = playerModel.playerSearchResult(
                id=row['id'],
                first_name=row['first_name'],
                last_name=row['last_name'],
                dob=row['DOB'] or "Unknown",
                team_name=row['team_name'],
                team_id=row['team_id'],
                position=row['position'],
                latestSeason=row['season']
            )
            players.append(player)
        
        return players 
    
    def playerProfile(self, id):
        query = """
        SELECT p.first_name, p.last_name, p.DOB, psm.position, psm.season, t.team_name
        FROM players p
        INNER JOIN playerSeasonMapping psm ON p.id = psm.player_id
        INNER JOIN teams t ON psm.team_id = t.team_id AND psm.season = t.season
        WHERE p.id = %s
        ORDER BY psm.season DESC
        """

        res = self.db.execute_query(query, (id,), fetch_results=True)

        if not res:
            return None
        
        firstRow = res[0]
        seasons = [row['season'] for row in res]

        return playerModel.playerProfile(
            first_name=firstRow['first_name'],
            last_name=firstRow['last_name'],
            dob=firstRow['DOB'] or "Unknown",
            current_team=firstRow['team_name'],
            curr_position=firstRow['position'],
            all_seasons=seasons
        )

    def playerEndOfSeason(self, id, season):
        query = """
        SELECT eos.*, p.first_name, p.last_name, p.DOB, psm.season, psm.fpl_season_id, psm.position, t.team_name
        FROM endOfSeason eos
        INNER JOIN players p ON eos.player_id = p.id
        INNER JOIN playerSeasonMapping psm ON eos.player_id = psm.player_id AND eos.season = psm.season
        INNER JOIN teams t ON psm.team_id = t.team_id AND psm.season = t.season
        WHERE p.id = %s AND psm.season = %s
        """

        res = self.db.execute_query(query, (id, season), fetch_results=True)

        if not res:
            return None

        firstRow = res[0]

        return playerModel.playerEndOfSeason(
            first_name=firstRow['first_name'],
            last_name=firstRow['last_name'],
            dob=firstRow['DOB'],
            season=firstRow['season'],
            fpl_season_id=firstRow['fpl_season_id'],
            position=firstRow['position'],
            team_name=firstRow['team_name'],
            total_points=firstRow['total_points'],
            goals_scored=firstRow['goals_scored'],
            assists=firstRow['assists'],
            minutes=firstRow['minutes'],
            own_goals=firstRow['own_goals'],
            penalties_missed=firstRow['penalties_missed'],
            penalties_order=firstRow['penalties_order'],
            penalties_saved=firstRow['penalties_saved'],
            points_per_game=firstRow['points_per_game'],
            points_per_game_rank=firstRow['points_per_game_rank'],
            expected_assists=firstRow['expected_assists'],
            expected_assists_per_90=firstRow['expected_assists_per_90'],
            expected_goal_involvements=firstRow['expected_goal_involvements'],
            expected_goal_involvements_per_90=firstRow['expected_goal_involvements_per_90'],
            expected_goals=firstRow['expected_goals'],
            expected_goals_per_90=firstRow['expected_goals_per_90'],
            expected_goals_conceded=firstRow['expected_goals_conceded'],
            expected_goals_conceded_per_90=firstRow['expected_goals_conceded_per_90'],
            yellow_cards=firstRow['yellow_cards'],
            red_cards=firstRow['red_cards'],
            bonus=firstRow['bonus'],
            bps=firstRow['bps'],
            saves=firstRow['saves'],
            saves_per_90=firstRow['saves_per_90'],
            influence=firstRow['influence'],
            creativity=firstRow['creativity'],
            creativity_rank=firstRow['creativity_rank'],
            threat=firstRow['threat'],
            ict_index=firstRow['ict_index'],
            cost=firstRow['cost'],
            selected_by_percent=firstRow['selected_by_percent'],
            selected_rank=firstRow['selected_rank'],
            starts=firstRow['starts'],
            starts_per_90=firstRow['starts_per_90'],
            transfers_in=firstRow['transfers_in'],
            transfers_out=firstRow['transfers_out']
        )



    def playerGameweekStats(self, id, season):
        query = """
        SELECT gws.*, t.team_name as opponent_team_name
        FROM gameweekStats gws
        INNER JOIN playerSeasonMapping psm ON psm.player_id = gws.player_id AND psm.season = gws.season
        INNER join teams t ON t.team_id = gws.opponent_team AND t.season = gws.season
        WHERE psm.player_id = %s AND psm.season = %s
        ORDER BY gws.gameweek
        """

        res = self.db.execute_query(query, (id, season), fetch_results=True)

        if not res:
            return None

        gameweeks = []
        for row in res:
            gw = playerModel.playerGameweekStats(
                player_id=id,
                season=season,
                gameweek=row['gameweek'],
                opponent_team=row['opponent_team'],
                opponent_name=row['opponent_team_name'],
                was_home=row['was_home'],
                round_points=row['round_points'],
                expected_assists=row['expected_assists'],
                expected_goal_involvements=row['expected_goal_involvements'],
                expected_goals=row['expected_goals'],
                expected_goals_conceded=row['expected_goals_conceded'],
                starts=row['starts'],
                transfers_in=row['transfers_in'],
                transfers_out=row['transfers_out'],
                minutes=row['minutes'],
                goals_scored=row['goals_scored'],
                assists=row['assists'],
                clean_sheets=row['clean_sheets'],
                goals_conceded=row['goals_conceded'],
                own_goals=row['own_goals'],
                penalties_saved=row['penalties_saved'],
                penalties_missed=row['penalties_missed'],
                yellow_cards=row['yellow_cards'],
                red_cards=row['red_cards'],
                saves=row['saves'],
                bonus=row['bonus'],
                bps=row['bps'],
                influence=row['influence'],
                creativity=row['creativity'],
                threat=row['threat'],
                ict_index=row['ict_index'],
                value=row['value'],
                selected=row['selected'],
                team_away_score=row['team_away_score'],
                team_home_score=row['team_home_score'],
            )
            gameweeks.append(gw)
        
        return gameweeks