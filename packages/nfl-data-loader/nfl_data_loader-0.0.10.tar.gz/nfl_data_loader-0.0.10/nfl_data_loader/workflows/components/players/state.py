import datetime

import pandas as pd

from nfl_data_loader.api.sources.events.games.games import get_schedules
from nfl_data_loader.api.sources.players.boxscores.boxscores import collect_weekly_espn_player_stats
from nfl_data_loader.api.sources.players.general.combine import collect_combine
from nfl_data_loader.api.sources.players.general.players import collect_players
from nfl_data_loader.api.sources.players.injuries.injuries import collect_injuries
from nfl_data_loader.api.sources.players.rosters.rosters import collect_roster, get_starters, collect_depth_chart
from nfl_data_loader.utils.formatters.general import df_rename_fold
from nfl_data_loader.utils.utils import find_year_for_season


class WeeklyPlayer:
    """
    Main class for extracting, merging, and building weekly states for NFL players.
    Handles roster, starter, injury, depth chart, and game participation data.
    For PoC, focuses on QBs.
    """
    def __init__(self, load_seasons, season_type=None):
        self.load_seasons = load_seasons
        self.season_type = season_type
        self.db = self.extract()
        self.team_events = self.static_team_events()
        #self.playerverse = self.init_playerverse()
        #self.df = self.run_pipeline()

        ### Create Player State

        ### Create Team State
        #### - GameID -> QB, RB, WR

    def extract(self):
        """
        Loads all raw data sources for the given seasons: schedule, rosters, injuries, starters, depth charts, stats, players, combine.
        Returns a dictionary of DataFrames.
        """
        """
        Extracting play by play data and weekly offensive player metrics
        Each of these data groups are extracted and loaded for the given seasons and filtered for the regular season
        :param load_seasons:
        :return:
        """
        ### Schedule
        print(f"    Loading schedule data {datetime.datetime.now()}")
        schedule = get_schedules(self.load_seasons, self.season_type)

        players = collect_players()

        ### Rosters
        print(f"    Loading weekly player roster data {datetime.datetime.now()}")
        rosters = pd.concat([collect_roster(season) for season in self.load_seasons])

        ### Injury Reports
        print(f"    Loading weekly player injury report data {datetime.datetime.now()}")
        injuries = pd.concat([collect_injuries(season) for season in self.load_seasons])

        ### Starters
        print(f"    Loading weekly player starter data {datetime.datetime.now()}")
        starters = pd.concat([get_starters(season) for season in self.load_seasons])

        ### Depth Charts
        print(f"    Loading weekly player depth chart data {datetime.datetime.now()}")
        depth_charts = pd.concat([collect_depth_chart(season) for season in self.load_seasons])

        ### Stats Weekly
        print(f"    Loading weekly player stats data {datetime.datetime.now()}")
        stats_weekly = collect_weekly_espn_player_stats(max(self.load_seasons), season_type=self.season_type).rename(columns={'recent_team': 'team'})
        stats_weekly = stats_weekly[stats_weekly.season.isin(self.load_seasons)].copy()

        print(f"    Loading defensive weekly player stats data {datetime.datetime.now()}")
        def_stats_weekly = collect_weekly_espn_player_stats(max(self.load_seasons), season_type=self.season_type, group='def')
        def_stats_weekly = def_stats_weekly[def_stats_weekly.season.isin(self.load_seasons)].copy()

        print(f"    Loading special teams weekly player stats data {datetime.datetime.now()}")
        kicking_stats_weekly = collect_weekly_espn_player_stats(max(self.load_seasons), season_type=self.season_type, group='kicking')
        kicking_stats_weekly = kicking_stats_weekly[kicking_stats_weekly.season.isin(self.load_seasons)].copy()

        return {
            'games': schedule,
            'rosters': rosters,
            'injuries': injuries,
            'starters': starters,
            'depth_charts': depth_charts,
            'player_stats': stats_weekly,
            'def_player_stats': def_stats_weekly,
            'kicking_player_stats': kicking_stats_weekly,
            'players': players,
        }

    def run_pipeline(self):
        """
        Main pipeline to process and merge all player data into weekly states.
        Returns a DataFrame of player-week states.
        """

        print(f"    Making Playerverse {datetime.datetime.now()}")

        ### Add game participants
        df = self.add_game_participants()

        ### Add events
        df = self.add_valid_games(df)

        ### Add injuries
        df = self.add_injuries(df)

        ## Add status
        df = self.transform_status(df)

        df = df[[
            'game_id',
            'player_id',
            'espn_id',
            'pfr_id',
            'season',
            'week',
            'team',
            'jersey_number',
            'high_pos_group',
            'position_group',
            'position',
            'depth_chart_position',
            'depth_chart_rank',
            #'depth_formation',
            'status',
            'report_status',
            'injury_designation',
            'playerverse_status'
        ]]
        return df

    def static_team_events(self):
        """
        Processes schedule data into team-level events, including game datetime and opponent info.
        Returns a DataFrame of team events.
        """
        event_df = self.db['games'].sort_values(
            by=['season', 'week', 'game_id'],
            ascending=[True, True, True]
        ).reset_index(drop=True)
        event_df['datetime'] = event_df['gameday'] + ' ' + event_df['gametime']
        event_df.datetime = pd.to_datetime(event_df.datetime)
        event_df['datetime'] = event_df['datetime'].fillna(event_df['gameday'])
        event_df.datetime = pd.to_datetime(event_df.datetime)
        event_df = event_df.drop(columns=['gametime'])
        ### Add 4 hrs to datetime column and then convert back to datetime in utc since were in ET
        event_df.datetime = event_df.datetime + pd.Timedelta(hours=4)
        event_df.datetime = pd.to_datetime(event_df.datetime, utc=True)
        event_df['away_opponent'] = event_df['home_team']
        event_df['home_opponent'] = event_df['away_team']
        event_df['is_home'] = event_df['home_team']

        fold_df = df_rename_fold(event_df, 'away_', 'home_').sort_values(
            by=['season', 'week', 'game_id'],
            ascending=[True, True, True]
        ).reset_index(drop=True)
        fold_df['is_home'] = fold_df['is_home'] == fold_df['team']

        return fold_df[[
            'game_id',
            'season',
            'game_type',
            'week',
            'datetime',
            'team',
            'opponent',
            'score',
            'rest',
            'qb_id',
            #'qb_name',
            #'coach',
            'is_home'
        ]]

    def _norm_id(self, s: pd.Series) -> pd.Series:
        # normalize to clean strings, not "nan"/"None", and strip trailing .0 from floaty ids
        s = s.astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        return s.replace({'nan': pd.NA, 'None': pd.NA, '': pd.NA})

    def _enrich_ids_from_players(self,rosters_df: pd.DataFrame, players: pd.DataFrame) -> pd.DataFrame:
        ro = rosters_df.copy()

        # 1) normalize all ID columns to string-like
        for df in (ro, players):
            for c in ('player_id', 'espn_id', 'pfr_id'):
                if c in df.columns:
                    df[c] = self._norm_id(df[c])

        # 2) make unique lookup maps for each key to avoid cartesian merges
        by_player = players.dropna(subset=['player_id']).drop_duplicates('player_id')[['player_id', 'espn_id', 'pfr_id']]
        by_espn = players.dropna(subset=['espn_id']).drop_duplicates('espn_id')[['espn_id', 'player_id', 'pfr_id']]
        by_pfr = players.dropna(subset=['pfr_id']).drop_duplicates('pfr_id')[['pfr_id', 'player_id', 'espn_id']]

        # 3) fill from player_id -> espn/pfr
        ro = ro.merge(
            by_player.rename(columns={'espn_id': '_espn_from_pid', 'pfr_id': '_pfr_from_pid'}),
            how='left', on='player_id'
        )
        ro['espn_id'] = ro['espn_id'].fillna(ro['_espn_from_pid'])
        ro['pfr_id'] = ro['pfr_id'].fillna(ro['_pfr_from_pid'])
        ro = ro.drop(columns=['_espn_from_pid', '_pfr_from_pid'])

        # 4) fill from espn_id -> player_id/pfr
        ro = ro.merge(
            by_espn.rename(columns={'player_id': '_pid_from_espn', 'pfr_id': '_pfr_from_espn'}),
            how='left', on='espn_id'
        )
        ro['player_id'] = ro['player_id'].fillna(ro['_pid_from_espn'])
        ro['pfr_id'] = ro['pfr_id'].fillna(ro['_pfr_from_espn'])
        ro = ro.drop(columns=['_pid_from_espn', '_pfr_from_espn'])

        # 5) fill from pfr_id -> player_id/espn
        ro = ro.merge(
            by_pfr.rename(columns={'player_id': '_pid_from_pfr', 'espn_id': '_espn_from_pfr'}),
            how='left', on='pfr_id'
        )
        ro['player_id'] = ro['player_id'].fillna(ro['_pid_from_pfr'])
        ro['espn_id'] = ro['espn_id'].fillna(ro['_espn_from_pfr'])
        ro = ro.drop(columns=['_pid_from_pfr', '_espn_from_pfr'])

        # final tidy
        ro = ro.drop_duplicates(['player_id', 'season', 'week', 'team', 'jersey_number']).reset_index(drop=True)
        return ro

    def add_game_participants(self):
        """
        Merges roster, starter, and stats info for each player-week-team.
        Returns a DataFrame with participation flags and metadata.
        """
        players = self.db['players'].copy()
        players = players[(players.last_season >= min(self.load_seasons))].copy()[[
            'player_id',
            'espn_id',
            'pfr_id',
        ]]

        ### Rosters
        rosters_df = self.db['rosters'][[
            'player_id',
            'espn_id',
            'pfr_id',
            'season',
            'week',
            'team',
            'high_pos_group',
            'position_group',
            'position',
            'depth_chart_position',
            'jersey_number',
            'status',
        ]]
        rosters_df = rosters_df[rosters_df.status != 'TRD'].copy()

        rosters_df = self._enrich_ids_from_players(rosters_df, players)

        starters_df = self.db['starters'].drop(columns=['game_id', 'game_type'])
        starters_df['espn_id'] = starters_df['espn_id'].astype(int)
        starters_df['espn_id'] = starters_df['espn_id'].astype(str)
        starters_df['played'] = starters_df['did_not_play'] == 0
        starters_df = starters_df.drop(columns=['did_not_play'])

        ## Will join starter in after we join roster + game participants
        rosters_df = rosters_df.merge(starters_df.drop(columns=['starter']), how='left', on=[
            'espn_id',
            'season',
            'week',
            'team'
        ]
                                      )
        rosters_df['rostered'] = True

        jersey_numbers = rosters_df[['player_id','espn_id','pfr_id', 'season', 'week', 'team', 'jersey_number','depth_chart_position',]].drop_duplicates(['player_id','espn_id','pfr_id', 'season', 'week', 'team', 'jersey_number','depth_chart_position',]).copy()

        ### Game Stats

        stats_df = pd.DataFrame()
        for groups in ['player_stats', 'def_player_stats', 'kicking_player_stats']:
            s = self.db[groups][[
                'player_id',
                'season',
                'week',
                'team',
                'high_pos_group',
                'position_group',
                'position',
                'status',
            ]].copy()
            s['played'] = True
            s['rostered'] = True
            stats_df = pd.concat([stats_df, s], axis=0).reset_index(drop=True)
            stats_df = stats_df.drop_duplicates(subset=[
                'player_id',
                'season',
                'week',
            ])
        stats_df = stats_df.merge(jersey_numbers, how='left', on=['player_id', 'season', 'week', 'team'])

        rosters_df = pd.concat([stats_df, rosters_df], axis=0).drop_duplicates(['player_id', 'season', 'week', 'team', 'jersey_number', 'position_group'], keep='last').reset_index(drop=True)

        ### Add depth charts

        depth_chart_df = self.db['depth_charts'][[
            'player_id',
            'season',
            'week',
            'team',
            'depth_chart_position',
            'depth_chart_rank',
            'depth_formation',
        ]]

        rosters_df['depth_formation'] = rosters_df['high_pos_group'].map({'off':'Offense','def':'Defense','st':'Special Teams'})

        rosters_df = rosters_df.merge(depth_chart_df.drop(columns=['depth_chart_position']), how='left', on=[
            'player_id',
            'season',
            'week',
            'team',
            'depth_formation',
        ])


        ### Add starters

        qb_starters_df = self.team_events[[
            'season',
            'week',
            'team',
            'qb_id',
        ]].rename(columns={'qb_id': 'player_id'})
        qb_starters_df['starter'] = True

        starters_df = pd.concat([qb_starters_df, starters_df.drop(columns=['played', 'espn_id'])], axis=0).drop_duplicates(['player_id', 'season', 'week', 'team'], keep='first').reset_index(drop=True)

        rosters_df = rosters_df.merge(starters_df, how='left', on=[
            'player_id',
            'season',
            'week',
            'team'
        ])

        return rosters_df

    def add_valid_games(self, df):
        """
        Flags valid games for each player-week-team by merging with team events.
        Returns a DataFrame with is_valid_game column.
        """
        events_df = self.team_events[[
            'game_id',
            'season',
            'week',
            'team',
            'datetime'
        ]].rename(columns={'datetime': 'game_datetime'})
        events_df['is_valid_game'] = True
        df = df.merge(events_df, how='left', on=[
            'season',
            'week',
            'team'
        ])
        return df

    def add_injuries(self, df):
        """
        Merges injury info and flags pre-kickoff injury designations for each player-week-team.
        Returns a DataFrame with injury columns.
        """
        if self.db['injuries'].shape[0] == 0:
            df['injury_designation'] = False
            df['pre_kickoff_injury_designation'] = False
            df['report_status'] = None
            #df['injury_report_date_modified'] = None
            return df



        injury_df = self.db['injuries'][[
            'player_id',
            'season',
            'team',
            'week',
            'report_primary_injury',
            'report_secondary_injury',
            'report_status',
            'practice_primary_injury',
            'practice_secondary_injury',
            'practice_status',
            'date_modified',
        ]].copy().rename(columns={
            'date_modified': 'injury_report_date_modified',
        })
        injury_df['injury_designation'] = True

        df = df.merge(injury_df, how='left', on=[
            'player_id',
            'season',
            'team',
            'week',
        ])
        df['game_datetime'] = pd.to_datetime(df.game_datetime)
        df['injury_report_date_modified'] = pd.to_datetime(df.injury_report_date_modified)
        df['pre_kickoff_injury_designation'] = df['game_datetime'] > df['injury_report_date_modified']
        ## Drop for now until we setup injury type
        df = df.drop(columns=['injury_report_date_modified', 'practice_status', 'practice_primary_injury', 'practice_secondary_injury','report_primary_injury', 'report_secondary_injury'])

        ### Need to clean this up and make injury type but for now this will do

        return df

    def transform_status(self, df):
        """
        Sets a status for each player-week (PLAYED, INJURED, ROSTERED, FREE_AGENT, RETIRED, NO_GAME).
        Returns a DataFrame with playerverse_status column. Allows for retirement, coming back from retirement, status is always captured for players for every week
        """
        ## status (PLAYED, INJURED, ROSTERED, FREE_AGENT, RETIRED)

        ## Create default status
        df['playerverse_status'] = 'NONE'
        ## Create known statuses for overrides

        ## If there is no game_id associated with the player default them to NO_GAME (can be overrided by RETIRED, FREE_AGENT)
        df.loc[((df['playerverse_status'] == 'NONE') & (df['game_id'].isnull())), 'playerverse_status'] = 'NO_GAME'
        ## If the player has the status of RET then they are retired
        df.loc[((df['status'] == 'RET')), 'playerverse_status'] = 'RETIRED'
        ## If the player has the report_status of OUT then they are injured
        df.loc[(((df['report_status'] == 'Out') & (df['injury_designation'] == True))), 'playerverse_status'] = 'INJURED'
        df.loc[((df['status'].isin(['INA']))), 'playerverse_status'] = 'INJURED'

        df.loc[((df['status'].isin(['ACT','RES']) )), 'playerverse_status'] = 'ROSTERED' # leaving like this in case I want to split out status

        ## If the player has stats then they played
        df.loc[((df['played'] == True)), 'playerverse_status'] = 'PLAYED'
        df.loc[((df['playerverse_status'] == 'NONE') & (df['status'].isin(['ACT','RES']) )), 'playerverse_status'] = 'ROSTERED' # leaving like this in case I want to split out status
        df.loc[((df['playerverse_status'] == 'NONE') & (df['rostered'] == True)), 'playerverse_status'] = 'ROSTERED'
        df.loc[((df['playerverse_status'] == 'NONE') | (df['status']=='CUT')), 'playerverse_status'] = 'FREE_AGENT'
        return df[df.playerverse_status!='NO_GAME'].copy()

    def add_event_qb_starters(self, df):
        """
        Flags QBs who started games using team events.
        Returns a DataFrame with starter flags for QBs.
        """

        starters_df = self.team_events[[
            'season',
            'week',
            'team',
            'qb_id',
        ]].rename(columns={'qb_id': 'player_id'})
        starters_df['events_qbs_played'] = True
        starters_df['events_qbs_starter'] = True
        df = df.merge(starters_df, how='left', on=[
            'player_id',
            'season',
            'week',
            'team'
        ]
        )
        # df['played'] = df['played'].fillna(df['events_qbs_played'])
        df = df.drop(columns=['events_qbs_played'])
        df['starter'] = df['starter'].fillna(df['events_qbs_starter'])
        df = df.drop(columns=['events_qbs_starter'])
        return df


if __name__ == '__main__':
    pdc = WeeklyPlayer(list(range(2020, 2025)))
    df = pdc.run_pipeline()