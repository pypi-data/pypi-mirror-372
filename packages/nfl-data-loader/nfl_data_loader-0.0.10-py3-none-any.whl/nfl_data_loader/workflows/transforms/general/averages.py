import numpy as np
import pandas as pd


def dynamic_window_ewma(x):
    """
    Calculate rolling exponentially weighted features with a dynamic window size
    """
    values = np.zeros(len(x))
    for i, (_, row) in enumerate(x.iterrows()):
        epa = x.epa_shifted[:i + 1]
        if row.week > 10:
            values[i] = epa.ewm(min_periods=1, span=row.week).mean().values[-1]
        else:
            values[i] = epa.ewm(min_periods=1, span=10).mean().values[-1]

    return pd.Series(values, index=x.index)


def dynamic_window_rolling_average(x, attr, mode='season_avg'):
    """
    Calculate rolling features with a dynamic window size for the specified attribute.

    Parameters:
        x (DataFrame): DataFrame containing the play-by-play data grouped by team.
        attr (str): The attribute for which rolling average is calculated.
        mode (str, optional): The mode of the rolling average. Default is 'season_avg'.

    Returns:
        pd.Series: Series with the dynamic rolling for the attribute.
    """
    values = np.zeros(len(x))
    attr_shifted = f'{attr}_shifted'

    for i, (_, row) in enumerate(x.iterrows()):
        attr_data = x[attr_shifted][:i + 1]
        if mode == 'career_avg':
            values[i] = attr_data.mean()
        elif mode == 'season_avg':
            if row['week'] != 1:
                values[i] = attr_data.rolling(min_periods=1, window=row['week'] - 1).mean().values[-1]
            else:
                # Handle edge case for the first week or season start
                values[i] = attr_data.rolling(min_periods=1, window=18 if row['season'] >= 2021 else 17).mean().values[-1]
        elif mode == 'season_total':
            if row['week'] != 1:
                values[i] = attr_data.rolling(min_periods=1, window=row['week'] - 1).sum().values[-1]
            else:
                # Handle edge case for the first week or season start
                values[i] = attr_data.rolling(min_periods=1, window=18 if row['season'] >= 2021 else 17).sum().values[-1]
        elif mode == 'form':
            ### last 3 divided by career avg
            values[i] = attr_data.rolling(min_periods=1, window=3).mean().values[-1]
        else:
            values[i] = attr_data.rolling(min_periods=1, window=3).mean().values[-1]

    return pd.Series(values, index=x.index)

def ensure_sorted_index(
    df,
    entity_cols='player_id',          # str or list/tuple of columns (e.g., ['team','position_group'])
    season_col='season',
    week_col='week',
    entity_name='player_id'           # internal name used for index level 0
):
    """
    Sort and set index for aligned vectorized ops.
    Index is always [entity_name, season_col, week_col].

    If `entity_cols` is a list/tuple (e.g., ['team','position_group']),
    we combine them into a single "entity" (stored in `entity_name`) using tuples,
    so grouping by level 0 treats the composite as one key.
    """
    df = df.copy()

    # Build/rename the first-level entity
    if isinstance(entity_cols, (list, tuple)):
        # tuple avoids string collisions and stays hashable
        df[entity_name] = list(zip(*[df[c].values for c in entity_cols]))
    else:
        if entity_cols != entity_name:
            df = df.rename(columns={entity_cols: entity_name})

    df = df.sort_values([entity_name, season_col, week_col]).copy()
    return df.set_index([entity_name, season_col, week_col])

def _shift_group(df_wide, cols):
    # shift all target cols by player
    g = df_wide.groupby(level=0, sort=False)  # level 0 -> player_id
    shifted = g[cols].shift()
    return shifted
def _within_season_expanding_sum_mean(shifted, how='mean'):
    """
    Vectorized within-season expanding over SHIFTED values:
    mean = csum_nonnull / ccount_nonnull (ignores NaNs),
    sum  = csum_nonnull.
    """
    # 1) force numeric (bad entries -> NaN)
    shifted_num = shifted.apply(pd.to_numeric, errors='coerce')

    # 2) non-null mask for counts
    nn = shifted_num.notna().astype(np.int64)

    # 3) season grouper = (entity at level 0, season at level 1)
    g_levels = [0, 1]

    # 4) cumsum over season (sum & count)
    csum = shifted_num.fillna(0).groupby(level=g_levels, sort=False).cumsum()
    ccnt = nn.groupby(level=g_levels, sort=False).cumsum()

    if how == 'sum':
        out = csum
    else:
        out = csum / ccnt
        out = out.where(ccnt > 0)
    return out


def _career_rolling_lastN(shifted, N):
    """
    Player-level rolling over SHIFTED values for all columns at once.
    """
    shifted_num = shifted.apply(pd.to_numeric, errors='coerce')
    g = shifted_num.groupby(level=0, sort=False)  # by entity (player/team/tuple)
    if np.isscalar(N):
        return (g[shifted_num.columns]
                .rolling(window=N, min_periods=1).mean()
                .reset_index(level=0, drop=True))
    else:
        roll17 = (g[shifted_num.columns]
                  .rolling(window=17, min_periods=1).mean()
                  .reset_index(level=0, drop=True))
        roll18 = (g[shifted_num.columns]
                  .rolling(window=18, min_periods=1).mean()
                  .reset_index(level=0, drop=True))
        return roll17, roll18


def _career_rolling_lastN_sum(shifted, N):
    shifted_num = shifted.apply(pd.to_numeric, errors='coerce')
    g = shifted_num.groupby(level=0, sort=False)
    if np.isscalar(N):
        return (g[shifted_num.columns]
                .rolling(window=N, min_periods=1).sum()
                .reset_index(level=0, drop=True))
    else:
        roll17 = (g[shifted_num.columns]
                  .rolling(window=17, min_periods=1).sum()
                  .reset_index(level=0, drop=True))
        roll18 = (g[shifted_num.columns]
                  .rolling(window=18, min_periods=1).sum()
                  .reset_index(level=0, drop=True))
        return roll17, roll18

def dynamic_window_all_attrs(
    df_grouped_weekly,
    attrs,
    mode='season_avg',
    entity_cols='player_id',      # str or list/tuple (e.g., ['team','position_group'])
    season_col='season',
    week_col='week',
    add_prefix=False              # keep for backwards-compat; set False (no prefixes)
):
    """
    Vectorized, multi-column dynamic rolling.
    Accepts any "entity" definition via `entity_cols`; internally the index is
    [player_id, season, week] where 'player_id' is either the true player id or a composite key.

    Returns: DataFrame with SAME index (no renaming/prefixing by default).
    """
    # Ensure expected index layout for downstream helpers that assume
    # index levels: 0->entity, 1->season, 2->week
    if (
        isinstance(df_grouped_weekly.index, pd.MultiIndex)
        and list(df_grouped_weekly.index.names) == ['player_id', season_col, week_col]
    ):
        df = df_grouped_weekly.copy()
    else:
        df = ensure_sorted_index(
            df_grouped_weekly,
            entity_cols=entity_cols,
            season_col=season_col,
            week_col=week_col,
            entity_name='player_id'
        )

    shifted = _shift_group(df, attrs)

    if mode == 'career_avg':
        g = shifted.groupby(level=0, sort=False)
        out = g[attrs].expanding(min_periods=1).mean().reset_index(level=0, drop=True)

    elif mode == 'form':
        g = shifted.groupby(level=0, sort=False)
        out = g[attrs].rolling(window=3, min_periods=1).mean().reset_index(level=0, drop=True)

    elif mode in ('season_avg','season_total'):
        within = _within_season_expanding_sum_mean(
            shifted, how=('sum' if mode=='season_total' else 'mean')
        )
        # Week-1 override: use career lastN (17 pre-2021, else 18)
        week = df.index.get_level_values(2).to_numpy()
        season = df.index.get_level_values(1).to_numpy()
        is_week1 = (week == 1)
        if is_week1.any():
            use18 = (season >= 2021)
            if mode == 'season_avg':
                roll17, roll18 = _career_rolling_lastN(shifted, N=[17,18])
            else:
                roll17, roll18 = _career_rolling_lastN_sum(shifted, N=[17,18])

            out = within.copy()
            pos = np.nonzero(is_week1)[0]
            out.iloc[pos] = np.where(use18[pos, None], roll18.iloc[pos], roll17.iloc[pos])
        else:
            out = within

    else:
        g = shifted.groupby(level=0, sort=False)
        out = g[attrs].rolling(window=3, min_periods=1).mean().reset_index(level=0, drop=True)

    if add_prefix:
        out = out.add_prefix(f'{mode}_')  # default: no prefix
    return out