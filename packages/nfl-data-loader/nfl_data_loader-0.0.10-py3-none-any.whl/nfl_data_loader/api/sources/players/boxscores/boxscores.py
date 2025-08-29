import pandas as pd

from nfl_data_loader.schemas.players.position import POSITION_MAPPER, HIGH_POSITION_MAPPER
from nfl_data_loader.utils.formatters.reformat_team_name import team_id_repl


def collect_weekly_player_stats(season, season_type=None):
    """

    :param season:
    :param week:
    :param season_type:
    :param group:
    :return:
    """
    try:
        data = pd.read_parquet(f'https://github.com/nflverse/nflverse-data/releases/download/stats_player/stats_player_week_{season}.parquet')
        if season_type is not None:
            data = data[((data.season_type == season_type))].copy()
        data = team_id_repl(data)
        data['position_group'] = data.position
        data.position_group = data.position_group.map(POSITION_MAPPER)
        data['high_pos_group'] = data.position_group
        data.high_pos_group = data.high_pos_group.map(HIGH_POSITION_MAPPER)
        data['status'] = 'ACT'
        data = data[data['position'].notnull()].copy()
        return data.drop(columns=['player_name',
         'player_display_name','headshot_url',])
    except Exception as e:
        return pd.DataFrame()


def collect_weekly_espn_player_stats(season, week=None, season_type=None,  group=''):
    """

    :param season:
    :param week:
    :param season_type:
    :param group:
    :return:
    """
    if group in ['def', 'kicking']:
        group = '_' + group
    data = pd.read_parquet(f'https://github.com/nflverse/nflverse-data/releases/download/player_stats/player_stats{group}.parquet')
    if week is not None:
        data = data[((data.season < season) | ((data.season == season) & (data.week <= week)))].copy()
    else:
        data = data[data.season <= season].copy()
    if season_type is not None:
        data = data[((data.season_type == season_type))].copy()
    data = team_id_repl(data)
    data['position_group'] = data.position
    data.position_group = data.position_group.map(POSITION_MAPPER)
    data['high_pos_group'] = data.position_group
    data.high_pos_group = data.high_pos_group.map(HIGH_POSITION_MAPPER)
    data['status'] = 'ACT'
    data = data[data['position'].notnull()].copy()
    return data.drop(columns=['player_name',
     'player_display_name','headshot_url',])

if __name__ == '__main__':
    df = collect_weekly_player_stats(2024, season_type=None)
    df


