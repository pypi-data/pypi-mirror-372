import pandas as pd

def get_player_fantasy_feature_store(season):
    try:
        df = pd.read_parquet(f'https://github.com/theedgepredictor/nfl-feature-store/raw/main/data/feature_store/player/fantasy/{season}.parquet')
        return df
    except:
        return pd.DataFrame()