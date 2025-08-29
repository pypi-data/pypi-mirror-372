import datetime
from dataclasses import dataclass, field
from typing import Dict, Optional, List, Tuple

import numpy as np
import pandas as pd

from nfl_data_loader.api.sources.events.games.games import get_schedules
from nfl_data_loader.api.sources.players.adv.fantasy.projections import get_player_fantasy_projections
from nfl_data_loader.api.sources.players.boxscores.boxscores import collect_weekly_player_stats
from nfl_data_loader.schemas.players.position import POSITION_MAPPER
from nfl_data_loader.utils.formatters.general import df_rename_shift, df_rename_exavg, df_rename_fold
from nfl_data_loader.workflows.transforms.general.averages import ensure_sorted_index, _shift_group, dynamic_window_all_attrs
from nfl_data_loader.workflows.transforms.general.general import _calculate_raw_passer_value, _calculate_passer_rating


METADATA = ['player_id', 'position', 'position_group', 'season', 'week', 'season_type', 'team', 'opponent_team',]

PASSING_COLS = ['completions', 'attempts', 'passing_yards', 'passing_tds', 'passing_interceptions', 'sacks_suffered', 'sack_yards_lost', 'sack_fumbles', 'sack_fumbles_lost', 'passing_air_yards', 'passing_yards_after_catch', 'passing_first_downs', 'passing_epa', 'passing_cpoe', 'passing_2pt_conversions', 'pacr',]

RUSHING_COLS = ['carries', 'rushing_yards', 'rushing_tds', 'rushing_fumbles', 'rushing_fumbles_lost', 'rushing_first_downs', 'rushing_epa', 'rushing_2pt_conversions',]

RECEIVING_COLS = [ 'receptions', 'targets', 'receiving_yards', 'receiving_tds', 'receiving_fumbles', 'receiving_fumbles_lost', 'receiving_air_yards', 'receiving_yards_after_catch', 'receiving_first_downs', 'receiving_epa', 'receiving_2pt_conversions', 'racr', 'target_share', 'air_yards_share', 'wopr',]

DEF_COLS = [ 'def_tackles_solo', 'def_tackles_with_assist', 'def_tackle_assists', 'def_tackles_for_loss', 'def_tackles_for_loss_yards', 'def_fumbles_forced', 'def_sacks', 'def_sack_yards', 'def_qb_hits', 'def_interceptions', 'def_interception_yards', 'def_pass_defended', 'def_tds', 'def_fumbles', 'def_safeties', 'misc_yards', 'fumble_recovery_own', 'fumble_recovery_yards_own', 'fumble_recovery_opp', 'fumble_recovery_yards_opp', 'fumble_recovery_tds', 'penalties', 'penalty_yards',]

ST_COLS = [
'punt_returns', 'punt_return_yards', 'kickoff_returns', 'kickoff_return_yards', 'special_teams_tds',
]

FANTASY_COLS = ['fantasy_points', 'fantasy_points_ppr',]

KICKING_COLS = [
    'fg_made',
    'fg_att',
    'fg_missed',
    'fg_blocked',
    'fg_long',
    'fg_pct',
    'fg_made_0_19',
    'fg_made_20_29',
    'fg_made_30_39',
    'fg_made_40_49',
    'fg_made_50_59',
    'fg_made_60_',
    'fg_missed_0_19',
    'fg_missed_20_29',
    'fg_missed_30_39',
    'fg_missed_40_49',
    'fg_missed_50_59',
    'fg_missed_60_',
    #'fg_made_list',
    #'fg_missed_list',
    #'fg_blocked_list',
    #'fg_made_distance',
    #'fg_missed_distance',
    #'fg_blocked_distance',
    'pat_made',
    'pat_att',
    'pat_missed',
    'pat_blocked',
    'pat_pct',
    'gwfg_made',
    'gwfg_att',
    'gwfg_missed',
    'gwfg_blocked',
    #'gwfg_distance',
]

ALL_NUM_COLS = (
    PASSING_COLS + RUSHING_COLS + RECEIVING_COLS +
    DEF_COLS + ST_COLS + FANTASY_COLS + KICKING_COLS
)

ENGINEERED_COLS = [
'net_passing_yards', 'total_plays', 'total_yards', 'total_fumbles', 'total_fumbles_lost', 'total_turnovers', 'total_touchdowns', 'total_first_downs', 'yards_per_pass_attempt', 'completion_percentage', 'sack_rate', 'fantasy_points_half_ppr', 'yards_per_rush_attempt', 'touchdown_per_play', 'yards_per_play', 'fantasy_point_per_play', 'air_yards_per_pass_attempt', 'VALUE_ELO', 'passer_rating'
]


# -----------------------------
# Utilities
# -----------------------------

def _to_num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")

def _g(df: pd.DataFrame, name: str, alt: Optional[str] = None) -> pd.Series:
    if name in df.columns:
        return _to_num(df[name]).fillna(0)
    if alt and alt in df.columns:
        return _to_num(df[alt]).fillna(0)
    return pd.Series(0.0, index=df.index)

def _safe_div(a: pd.Series, b: pd.Series) -> pd.Series:
    b = _to_num(b).replace(0, np.nan)
    return _to_num(a) / b

def _score_kickers_nfl(df: pd.DataFrame, include_blocked_as_missed: bool = True) -> pd.Series:
    # +1 PAT made; -1 FG missed; +3 FG 0–39; +4 FG 40–49; +5 FG 50–59 and 60+
    pts = _g(df, "pat_made") * 1.0

    fg0_39_made = _g(df, "fg_made_0_19") + _g(df, "fg_made_20_29") + _g(df, "fg_made_30_39")
    pts += fg0_39_made * 3.0
    pts += _g(df, "fg_made_40_49") * 4.0
    pts += (_g(df, "fg_made_50_59") + _g(df, "fg_made_60_")) * 5.0

    misses = (
        _g(df, "fg_missed_0_19") + _g(df, "fg_missed_20_29") + _g(df, "fg_missed_30_39") +
        _g(df, "fg_missed_40_49") + _g(df, "fg_missed_50_59") + _g(df, "fg_missed_60_")
    )
    if include_blocked_as_missed:
        misses += _g(df, "fg_blocked")

    pts -= misses * 1.0
    return pts.astype(float)


def _normalize_core_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize common columns that appear with slightly different names across sources.
    Adds sane defaults if missing.
    """
    df = df.copy()

    # sacks / sack yards
    if "sacks" not in df.columns:
        df["sacks"] = _g(df, "sacks_suffered").values
    if "sack_yards" not in df.columns:
        df["sack_yards"] = _g(df, "sack_yards_lost").values

    # interceptions (passing)
    if "interceptions" not in df.columns:
        df["interceptions"] = _g(df, "passing_interceptions").values
    if "passing_interceptions" not in df.columns:
        df["passing_interceptions"] = _g(df, "interceptions").values

    # convenience: completions/attempts exist in most sources
    for c in ["completions","attempts","passing_yards","passing_tds"]:
        if c not in df.columns:
            df[c] = 0.0

    # receiving_air_yards often used for rates
    if "receiving_air_yards" not in df.columns:
        df["receiving_air_yards"] = 0.0

    return df


def _derive_boxscore_metrics(df: pd.DataFrame, mode) -> pd.DataFrame:
    """
    Derive standardized team/group/player metrics on a weekly aggregated frame.
    Requires columns normalized via _normalize_core_columns first.
    """
    df = df.copy()

    df["net_passing_yards"] = _g(df, "passing_yards") - _g(df, "sack_yards")
    if mode == 'Team':
        df["total_plays"] = _g(df, "attempts") + _g(df, "sacks") + _g(df, "carries")
        df["total_yards"] = _g(df, "rushing_yards") + _g(df, "passing_yards")
        df["total_touchdowns"] = _g(df, "passing_tds") + _g(df, "rushing_tds") + _g(df, "special_teams_tds")
        df["total_first_downs"] = _g(df, "passing_first_downs") + _g(df, "rushing_first_downs")
        df["air_yards_per_pass_attempt"] = _safe_div(_g(df, "receiving_air_yards"), _g(df, "attempts"))
    else:
        df["total_plays"] = _g(df, "attempts") + _g(df, "sacks") + _g(df, "carries") + _g(df, "receptions")
        df["total_yards"] = _g(df, "rushing_yards") + _g(df, "passing_yards") + _g(df, 'receiving_yards')
        df["total_touchdowns"] = _g(df, "passing_tds") + _g(df, "rushing_tds") + _g(df, "special_teams_tds") + _g(df, 'receiving_tds')
        df["total_first_downs"] = _g(df, "passing_first_downs") + _g(df, "rushing_first_downs") + _g(df, 'receiving_first_downs')
        df["air_yards_per_pass_attempt"] = _safe_div(_g(df, "receiving_air_yards") + _g(df, "passing_air_yards"), _g(df, "attempts"))

    df["total_fumbles"] = _g(df, "rushing_fumbles") + _g(df, "receiving_fumbles") + _g(df, "sack_fumbles")
    df["total_fumbles_lost"] = _g(df, "rushing_fumbles_lost") + _g(df, "receiving_fumbles_lost") + _g(df, "sack_fumbles_lost")
    df["total_turnovers"] = _g(df, "total_fumbles_lost") + _g(df, "interceptions")


    df["yards_per_pass_attempt"] = _safe_div(_g(df, "passing_yards"), _g(df, "attempts"))
    df["completion_percentage"] = _safe_div(_g(df, "completions"), _g(df, "attempts"))
    df["sack_rate"] = _safe_div(_g(df, "sacks"), _g(df, "attempts"))

    df["fantasy_points_half_ppr"] = _g(df, "fantasy_points") + _g(df, "receptions") * 0.5

    df["yards_per_rush_attempt"] = _safe_div(_g(df, "rushing_yards"), _g(df, "carries"))
    df["touchdown_per_play"] = _safe_div(_g(df, "total_touchdowns"), _g(df, "total_plays"))
    df["yards_per_play"] = _safe_div(_g(df, "total_yards"), _g(df, "total_plays"))
    df["fantasy_point_per_play"] = _safe_div(_g(df, "fantasy_points_ppr"), _g(df, "total_plays"))


    # passer value and rating (safe to call; missing cols were normalized above)
    try:
        df["VALUE_ELO"] = _calculate_raw_passer_value(df)
    except Exception:
        df["VALUE_ELO"] = np.nan
    try:
        df["passer_rating"] = _calculate_passer_rating(df)
    except Exception:
        df["passer_rating"] = np.nan

    return df


def _map_projection_columns_to_boxscore(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create boxscore-like columns from the projections dataframe.
    Only sets columns where a mapping is obvious; others default to 0.
    """
    if df.shape[0] == 0:
        return df
    df = df.copy()
    colmap = {
        # Passing
        "projected_passing_attempts": "attempts",
        "projected_passing_completions": "completions",
        "projected_passing_yards": "passing_yards",
        "projected_passing_touchdowns": "passing_tds",
        "projected_passing_interceptions": "interceptions",
        #"projected_passing_completion_percentage": "completion_percentage",
        # Rushing
        "projected_rushing_attempts": "carries",
        "projected_rushing_yards": "rushing_yards",
        "projected_rushing_touchdowns": "rushing_tds",
        "projected_rushing2_pt_conversions": "rushing_2pt_conversions",
        # Receiving
        "projected_receiving_receptions": "receptions",
        "projected_receiving_targets": "targets",
        "projected_receiving_yards": "receiving_yards",
        "projected_receiving_touchdowns": "receiving_tds",
        "projected_receiving2_pt_conversions": "receiving_2pt_conversions",
        # Kicking / ST
        "projected_made_extra_points": "pat_made",
        "projected_attempted_extra_points": "pat_att",
        "projected_missed_extra_points": "pat_missed",
        "projected_made_field_goals": "fg_made",
        "projected_attempted_field_goals": "fg_att",
        "projected_missed_field_goals": "fg_missed",
        "projected_made_field_goals_from50_plus": "fg_made_50_59",  # 60+ not always split
        "projected_made_field_goals_from40_to49": "fg_made_40_49",
        "projected_made_field_goals_from_under40": "fg_made_30_39",  # approx bucket
        # Engineered

    }
    for src, tgt in colmap.items():
        if src in df.columns:
            df[tgt] = _to_num(df[src])
        else:
            if tgt not in df.columns:
                df[tgt] = 0.0

    # Fantasy points are already provided as 'projected_points'
    df["fantasy_points_ppr"] = df["projected_points"].fillna(0) + df["receptions"].fillna(0) * 0.5
    df["fantasy_points"] = df["projected_points"].fillna(0) - df["receptions"].fillna(0) * 0.5
    return df


# -----------------------------
# Core dataclasses
# -----------------------------

@dataclass
class WeeklyStatCollection:
    season_type: str = "REG"
    offensive: bool = True
    mode: str = "Team"                 # Team | PlayerGroup | Player
    type: str = "Average"              # Actual | Average | Expected | Projected
    agg: str = "season_avg"            # season_avg | season_total | form | career_avg | last | actual
    keys: Tuple[str, ...] = ("team","season","week")  # identifier cols present in `frame`
    attrs: List[str] = field(default_factory=list)     # numeric attrs the frame contains
    frame: Optional[pd.DataFrame] = None
    meta: Dict = field(default_factory=dict)           # anything else (source, version, notes, etc.)


# -----------------------------
# Main component
# -----------------------------

class WeeklyBoxscoreComponent:
    """
    End-to-end:
      1) extract(): schedules + weekly player stats
      2) make_stat_collection(mode): build weekly aggregates (team / opp / player_group / opp_player_group / player)
      3) build_collections(): compute family of (mode, type, agg) DataFrames using dynamic_window_all_attrs
    """

    def __init__(self, load_seasons: List[int], season_type: Optional[str] = "REG"):
        self.load_seasons = load_seasons
        self.season_type = season_type
        self.db = self.extract()
        self.skill_groups = ["quarterback", "o_pass", "o_rush", "o_te"]  # not strictly required but kept
        self.collections = {}

    # ---------- Extraction ----------

    def extract(self) -> Dict[str, pd.DataFrame]:
        print(f"    Loading schedules & player stats @ {datetime.datetime.now()}")
        schedule = get_schedules(self.load_seasons, self.season_type)
        player_stats = pd.concat([
            collect_weekly_player_stats(season, season_type=self.season_type)
            for season in self.load_seasons
        ], ignore_index=True)

        projections = pd.concat([
            get_player_fantasy_projections(season, mode = "weekly", group = "All",
                        score_mode= "HALF")
            for season in self.load_seasons
        ], ignore_index=True)

        return {
            "games": schedule,
            "player_stats": player_stats,
            "projections": _map_projection_columns_to_boxscore(projections)
        }

    # ---------- Core builders ----------

    def _apply_kicker_scoring(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        if "position" in df.columns:
            mask_k = df["position"] == "K"
            if mask_k.any():
                df.loc[mask_k, "fantasy_points"] = _score_kickers_nfl(df.loc[mask_k].copy())
                df.loc[mask_k, "fantasy_points_ppr"] = df.loc[mask_k, "fantasy_points"]
        return df

    def _expand_schedule_team_rows_opp(self,df) -> pd.DataFrame:
        """season, week, team, opponent for REG games across seasons."""
        sched = self.db['games'].copy()
        sched = sched[sched["season"].isin(self.load_seasons)].copy()
        sched = sched[sched["game_type"] == "REG"].copy()
        home = sched[["season", "week", "home_team", "away_team"]].rename(
            columns={"home_team": "team", "away_team": "opponent"})
        away = sched[["season", "week", "home_team", "away_team"]].rename(
            columns={"away_team": "team", "home_team": "opponent"})
        out = pd.concat([home, away], ignore_index=True)

        out["week"] = out["week"].astype(int)
        out = out.sort_values(["season", "week", "team"]).reset_index(drop=True)
        return df.merge(
                out.rename(columns={"opponent":"opponent_team"}),
                on=["season","week","team"],
                how="left"
            )

    def _projected_to_actual_format(self, df):
        df = self._expand_schedule_team_rows_opp(df)


    def make_stat_collection(self, stat_mode: str, projected=False) -> pd.DataFrame:
        """
        Build weekly aggregates for a specific mode:
          - 'team'                     → groupby ['season','week','team']
          - 'opponent'                 → groupby ['season','week','opponent_team'] (renamed to 'team')
          - 'player_group'             → groupby ['season','week','team','position_group']
          - 'opponent_player_group'    → groupby ['season','week','opponent_team','position_group'] (→ team)
          - 'player'                   → groupby ['season','week','player_id','position','team']
        """
        if projected:
            df = self.db["projections"].copy()
            df['position_group'] = df['position'].map(POSITION_MAPPER)
            df = self._expand_schedule_team_rows_opp(df)
        else:
            df = self.db["player_stats"].copy()
            df = _normalize_core_columns(df)
            df = self._apply_kicker_scoring(df)

        numeric_cols_present = [c for c in ALL_NUM_COLS +(ENGINEERED_COLS if projected else []) if c in df.columns]

        if stat_mode in ["team", "opponent"]:
            key = "team" if stat_mode == "team" else "opponent_team"
            gcols = ["season", "week", key]
            agg = df.groupby(gcols, as_index=False)[numeric_cols_present].sum()
            # count distinct players in the group
            cnt = (df
                   .groupby(gcols, as_index=False)["player_id"]
                   .nunique()
                   .rename(columns={"player_id": "n_players"}))

            agg = agg.merge(cnt, on=gcols, how="left")
            agg = agg.rename(columns={key: "team"})
        elif stat_mode in ["player_group", "opponent_player_group"]:
            key = "team" if stat_mode == "player_group" else "opponent_team"
            gcols = ["season", "week", key, "position_group"]
            agg = df.groupby(gcols, as_index=False)[numeric_cols_present].sum()
            cnt = (df
                   .groupby(gcols, as_index=False)["player_id"]
                   .nunique()
                   .rename(columns={"player_id": "n_players"}))

            agg = agg.merge(cnt, on=gcols, how="left")
            agg = agg.rename(columns={key: "team"})
        elif stat_mode == "player":
            # keep identity columns on the groupby to preserve metadata
            gcols = ["season", "week", "player_id", "position", "team"]
            agg = df.groupby(gcols, as_index=False)[numeric_cols_present].sum()
        else:
            raise ValueError(f"Unknown stat_mode: {stat_mode}")

        if not projected:
            agg = _normalize_core_columns(agg)
            agg = _derive_boxscore_metrics(agg, mode= 'Team' if stat_mode in ["team", "opponent"] else 'Player')
        return agg

    # ---------- Dynamic aggregations ----------

    def _dynamic_for_keys(self, df: pd.DataFrame, keys: List[str], attrs: List[str], agg_mode: str) -> pd.DataFrame:
        """
        keys:
          Team         -> ['team','season','week']
          PlayerGroup  -> ['team','position_group','season','week']
          Player       -> ['player_id','season','week']
        Produces NO prefixes; keeps keys as columns.
        """
        # split keys into entity + time
        if len(keys) == 3:
            entity_cols = keys[0]
            season_col, week_col = keys[1], keys[2]
        elif len(keys) == 4:
            entity_cols = [keys[0], keys[1]]
            season_col, week_col = keys[2], keys[3]
        else:
            raise ValueError("keys must be length 3 or 4")

        base = df[keys + attrs].copy()

        out = dynamic_window_all_attrs(
            base, attrs, mode=agg_mode,
            entity_cols=entity_cols, season_col=season_col, week_col=week_col,
            add_prefix=False  # <- no prefixes
        ).reset_index()

        # Expand composite entity (tuple) back into separate columns
        if isinstance(entity_cols, (list, tuple)):
            ent_df = pd.DataFrame(out['player_id'].tolist(), columns=list(entity_cols), index=out.index)
            out = pd.concat([ent_df, out.drop(columns=['player_id'])], axis=1)
        else:
            out = out.rename(columns={'player_id': entity_cols})

        return out

    def _last_values(self, df: pd.DataFrame, keys: List[str], attrs: List[str]) -> pd.DataFrame:
        if len(keys) == 3:
            entity_cols = keys[0]
            season_col, week_col = keys[1], keys[2]
        else:
            entity_cols = [keys[0], keys[1]]
            season_col, week_col = keys[2], keys[3]

        base = df[keys + attrs].copy()
        base_idx = ensure_sorted_index(base, entity_cols=entity_cols, season_col=season_col, week_col=week_col, entity_name='player_id')
        shifted = _shift_group(base_idx, attrs).reset_index()

        if isinstance(entity_cols, (list, tuple)):
            ent_df = pd.DataFrame(shifted['player_id'].tolist(), columns=list(entity_cols), index=shifted.index)
            shifted = pd.concat([ent_df, shifted.drop(columns=['player_id'])], axis=1)
        else:
            shifted = shifted.rename(columns={'player_id': entity_cols})

        return shifted
    
    def _fold_for_exavg(self, team, opponent, mode='Team'):
        if mode == 'Team':
            filters = [ "season", "week"]
            entity_cols = ['team']
            keys = filters + entity_cols
        elif mode == 'PlayerGroup':
            filters = [ "season", "week"]
            entity_cols = ['team','position_group']
            keys = filters + entity_cols
        else:
            raise Exception('Not valid')

        away_merge_cols = [f"away_{i}" if i == 'team' else i for i in entity_cols]
        home_merge_cols = [f"home_{i}" if i == 'team' else i for i in entity_cols]

        game_features_df = self.db['games'][['home_team','away_team', 'season', 'week','home_score','away_score']]

        # symmetrical columns are passed in offensive
        offensive_cols = PASSING_COLS + RUSHING_COLS + RECEIVING_COLS + FANTASY_COLS + KICKING_COLS + ENGINEERED_COLS + ([] if mode == 'Player' else ['n_players'])
        defensive_cols = DEF_COLS + ST_COLS

        team_features_df = pd.merge(
            team[keys + offensive_cols + defensive_cols],
            opponent[keys + offensive_cols + defensive_cols],
            on=keys,
            suffixes=('_offense', '_defense')
        )

        df = game_features_df.merge(
            team_features_df.rename(columns={'team': 'home_team'}),
            on=['home_team']+filters, ### Join to event ['home_team', 'away_team']
            how='left'
        ).merge(
            team_features_df.rename(columns={'team': 'away_team'}),
            on=away_merge_cols+filters, ### Join to specific entity filter
            how='left',
            suffixes=('_home', '_away')
        )

        # Suffix to prefix
        df.columns = [
            'home_' + col.replace('_home', '') if '_home' in col and 'actual_' not in col else
            'away_' + col.replace('_away', '') if '_away' in col and 'actual_' not in col else
            col
            for col in df.columns
        ]

        df = df.dropna(subset=['home_score', 'away_score'])

        inference_df = game_features_df[((game_features_df.home_score.isnull()) & (game_features_df.away_score.isnull()))].copy()
        latest_epa = team_features_df.groupby(entity_cols).nth(-1).drop(columns=filters)

        inference_df = inference_df.merge(
            latest_epa.rename(columns={'team': 'home_team'}),
            on=['home_team'], ### Join to event ['home_team', 'away_team']
            how='left'
        ).merge(
            latest_epa.rename(columns={'team': 'away_team'}),
            on=away_merge_cols, ### Join to specific entity filter
            how='left',
            suffixes=('_home', '_away')
        )

        # Suffix to prefix
        inference_df.columns = [
            'home_' + col.replace('_home', '') if '_home' in col and 'actual_' not in col else
            'away_' + col.replace('_away', '') if '_away' in col and 'actual_' not in col else
            col
            for col in inference_df.columns
        ]

        df = pd.concat([df, inference_df])

        columns_for_base = filters + home_merge_cols + away_merge_cols

        columns_for_shift = ['is_home'] + list(team_features_df.columns)

        base_dataset_df = df[columns_for_base].copy()
        shifted_df = df_rename_shift(df)[columns_for_shift]

        #### Rename for Expected Average
        t1_cols = [i for i in shifted_df.columns if '_offense' in i and (i not in keys) and i.replace('home_', '') in columns_for_shift]
        t2_cols = [i for i in shifted_df.columns if '_defense' in i and (i not in keys) and i.replace('away_', '') in columns_for_shift]

        #### Apply Expected Average
        expected_features_df = df_rename_exavg(shifted_df, '_offense', '_defense', t1_cols=t1_cols, t2_cols=t2_cols)

        #### Fold base from away and home into team
        folded_dataset_df = base_dataset_df.copy()
        folded_dataset_df = df_rename_fold(folded_dataset_df, 'away_', 'home_')
        folded_dataset_df = pd.merge(folded_dataset_df, expected_features_df, on=keys, how='left')
        folded_dataset_df.columns = [i.replace('exavg_','') for i in folded_dataset_df.columns]
        return folded_dataset_df.drop(columns=['is_home'])

    def _add_dynamic_aggregations_future(self, team_features_df, entities, filters):
        game_features_df = df_rename_fold(self.db['games'][['home_team','away_team', 'season', 'week','home_score','away_score']], 'home_','away_')
        game_features_df = game_features_df[game_features_df.score.isnull()].drop(columns=['score']).copy()
        if game_features_df.shape[0] == 0:
            return team_features_df.sort_values(entities+filters) # no future games.

        latest_agg = team_features_df.groupby(entities).nth(-1).drop(columns=filters)
        inference_df = game_features_df.merge(
            latest_agg,
            on=['team'],
            how='left'
        )
        return pd.concat([team_features_df, inference_df], ignore_index=True).sort_values(entities+filters)

    def make_dynamic_aggregations(self,
                                  base_df: pd.DataFrame,
                                  mode: str,
                                  attrs: Optional[List[str]] = None,
                                  aggs: Optional[List[str]] = None) -> Dict[str, pd.DataFrame]:
        """
        Given a base weekly df for a mode, compute multiple aggregation windows.
        Returns dict of agg_mode → dataframe merged onto keys + attrs' derived names.
        """
        if attrs is None:
            # choose numeric attr columns that exist
            attrs = [c for c in ALL_NUM_COLS+ENGINEERED_COLS + ([] if mode == 'Player' else ['n_players']) if c in base_df.columns]

        if aggs is None:
            aggs = ["season_avg", "season_total", "form", "career_avg", "last"]


        if mode == "Team":
            keys = ["team", "season", "week"]
            entities = ['team']
            filters = ['season', 'week']
        elif mode == "PlayerGroup":
            keys = ["team", "position_group", "season", "week"]
            entities = ['team',"position_group"]
            filters = ['season', 'week']
        elif mode == "Player":
            keys = ["team","player_id", "season", "week"]
            entities = ['team',"player_id"]
            filters = ['season', 'week']
        else:
            raise ValueError(f"Unknown mode {mode}")

        # Ensure we keep only needed columns to reduce memory
        df = base_df[keys + attrs].copy()

        out_frames: Dict[str, pd.DataFrame] = {}

        for agg_mode in aggs:
            if agg_mode == "last":
                last_df = self._last_values(df, keys, attrs)
                out_frames[agg_mode] = self._add_dynamic_aggregations_future(last_df, entities, filters)
            elif agg_mode in {"season_avg", "season_total", "form", "career_avg"}:
                # Use the vectorized helper
                agg_df = self._dynamic_for_keys(df, keys, attrs, agg_mode)
                out_frames[agg_mode] = self._add_dynamic_aggregations_future(agg_df, entities, filters)
            else:
                # skip unknown agg types
                continue

        return out_frames

    # ---------- High-level orchestrators ----------

    def _build_group_mode_collections(self, mode = 'PlayerGroup', team_agg_types= ['season_avg', 'form', 'last']):
        """
        1. Metadata: Define metadata for Collection Mode
        2. Actual: Compute the trivial "Actual" Weekly boxscore stats and save as a collection
        3. Average: Compute rolling "Average" Weekly boxscore stats and save a collection for each agg type
        4. Expected: Compute "Expected" Weekly boxscore stats from Average -> 'season_avg' agg (see notes on Expected stats)
        5. Projected: Compute the "Projected" Weekly boxscore stats from ESPN fantasy projections
        :return:
        """

        # Average / Expected (dynamic windows) – compute for both offense and defense and suffix columns

        team_weekly = self.make_stat_collection("player_group" if mode == 'PlayerGroup' else 'team')
        opp_weekly = self.make_stat_collection("opponent_player_group" if mode == 'PlayerGroup' else 'opponent')

        actual_team = WeeklyStatCollection(
            season_type=self.season_type, offensive=True, mode=mode, type="Actual", agg="actual",
            frame=team_weekly.copy()
        )
        actual_opp = WeeklyStatCollection(
            season_type=self.season_type, offensive=False, mode=mode, type="Actual", agg="actual",
            frame=opp_weekly.rename(columns={"team": "team"}).copy()
        )

        actual_collections = {
            "team": actual_team,
            "opponent": actual_opp,
        }

        team_aggs = self.make_dynamic_aggregations(team_weekly, mode=mode, aggs=team_agg_types)
        opp_aggs = self.make_dynamic_aggregations(opp_weekly, mode=mode, aggs=team_agg_types)

        avg_collections = {}
        expected_collections = {}
        for agg_name, off_df in team_aggs.items():
            # merge offense + defense on keys
            def_df = opp_aggs[agg_name]
            avg_team = WeeklyStatCollection(
                season_type=self.season_type,
                offensive=True,
                mode=mode,
                type="Average",
                agg=agg_name,
                frame=off_df.copy()
            )
            avg_opponent = WeeklyStatCollection(
                season_type=self.season_type,
                offensive=False,
                mode=mode,
                type="Average",
                agg=agg_name,
                frame=def_df.copy()
            )
            if agg_name == 'season_avg' and mode == 'Team': ### Skipping Expected for PlayerGroup currently until we figure out what we want to do here
                exavg_df = self._fold_for_exavg(off_df.copy(), def_df.copy(), mode)
                exavg_team = WeeklyStatCollection(
                    season_type=self.season_type, offensive=True, mode=mode, type="Expected", agg=agg_name,
                    frame=exavg_df.copy()
                )
                expected_collections[agg_name] = {
                    'team':exavg_team
                }

            avg_collections[agg_name] = {
                'team': avg_team,
                'opponent': avg_opponent,
            }


        team_weekly_projected = self.make_stat_collection("player_group" if mode == 'PlayerGroup' else 'team', projected=True)
        opp_weekly_projected = self.make_stat_collection("opponent_player_group" if mode == 'PlayerGroup' else 'opponent', projected=True)

        projected_team = WeeklyStatCollection(
            season_type=self.season_type, offensive=True, mode=mode, type="Projected", agg="actual",
            frame=team_weekly_projected.copy()
        )
        projected_opponent = WeeklyStatCollection(
            season_type=self.season_type, offensive=False, mode=mode, type="Projected", agg="actual",
            frame=opp_weekly_projected.rename(columns={"team": "team"}).copy()
        )

        projected_collections = {
            "team": projected_team,
            "opponent": projected_opponent,
        }
        return {
            "Actual": actual_collections,
            "Average": avg_collections,
            "Expected": expected_collections,
            "Projected": projected_collections
        }

    def _build_player_mode_collections(self,team_agg_types= ['season_avg', 'form', 'last']):
        """
                1. Metadata: Define metadata for Collection Mode
                2. Actual: Compute the trivial "Actual" Weekly boxscore stats and save as a collection
                3. Average: Compute rolling "Average" Weekly boxscore stats and save a collection for each agg type
                4. Expected: Compute "Expected" Weekly boxscore stats from Average -> 'season_avg' agg (see notes on Expected stats)
                5. Projected: Compute the "Projected" Weekly boxscore stats from ESPN fantasy projections
                :return:
                """

        # Average / Expected (dynamic windows) – compute for both offense and defense and suffix columns

        team_weekly = self.make_stat_collection("player")

        actual_team = WeeklyStatCollection(
            season_type=self.season_type, offensive=True, mode='Player', type="Actual", agg="actual",
            frame=team_weekly.copy()
        )

        actual_collections = {
            "team": actual_team,
        }

        team_aggs = self.make_dynamic_aggregations(team_weekly, mode='Player', aggs=team_agg_types)

        avg_collections = {}
        expected_collections = {}
        for agg_name, off_df in team_aggs.items():
            # merge offense + defense on keys
            avg_team = WeeklyStatCollection(
                season_type=self.season_type,
                offensive=True,
                mode='Player',
                type="Average",
                agg=agg_name,
                frame=off_df.copy()
            )

            avg_collections[agg_name] = {
                'team': avg_team,
            }

        team_weekly_projected = self.make_stat_collection("player", projected=True)

        projected_team = WeeklyStatCollection(
            season_type=self.season_type, offensive=True, mode='Player', type="Projected", agg="actual",
            frame=team_weekly_projected.copy()
        )

        projected_collections = {
            "team": projected_team,
        }
        return {
            "Actual": actual_collections,
            "Average": avg_collections,
            "Expected": expected_collections,
            "Projected": projected_collections
        }

    def build_collections(self, team=True, player_group=True, player = True):
        """
        Build full set of stat collections for (Mode → Type → Agg).
        Types:
          - Actual: raw weekly
          - Average: rolling/expanding windows ('season_avg','season_total','form','career_avg','last')
          - Expected: alias to Average('season_avg') by default (can be replaced with xPass/xRush later)
          - Projected: pulls projections and normalizes to boxscore schema
        """

        team_collections = {} if not team else self._build_group_mode_collections(mode='Team', team_agg_types=['season_avg', 'form', 'last'])
        player_group_collections = {} if not player_group else self._build_group_mode_collections(mode='PlayerGroup', team_agg_types=['season_avg', 'form', 'last'])
        player_collections = {} if not player else self._build_player_mode_collections(team_agg_types=['season_avg', 'form', 'last'])
        self.collections = {
            "Team": team_collections,
            "PlayerGroup": player_group_collections,
            "Player": player_collections,
        }

    def make_view(self, mode, filters: dict):
        """
        Flatten the built collections for a given mode into one filtered DataFrame.

        Metadata columns added:
          - collection: "<Mode>.<Type>[.<Agg>].<group>"
          - season_type
          - type: Actual | Average | Expected | Projected
          - agg: season_avg | form | last | season_total | career_avg | actual (when applicable)
          - group: "team" | "opponent"
          - mode

        filters example:
          {"season": 2025, "week": 1, "team": "BUF"}  # can include type/agg too since we add them before filtering
        """
        import pandas as pd

        def _apply_filters(df, filt: dict):
            if not filt:
                return df
            out = df.copy()
            for k, v in filt.items():
                if k not in out.columns:
                    continue
                if isinstance(v, (list, tuple, set)):
                    out = out[out[k].isin(list(v))]
                else:
                    out = out[out[k].isna()] if v is None else out[out[k] == v]
            return out

        def _append_with_meta(sc_obj, group_label: str, bucket_type: str, agg_name: str | None):
            if sc_obj is None or sc_obj.frame is None or sc_obj.frame.empty:
                return
            df = sc_obj.frame.copy()
            df["mode"] = sc_obj.mode
            df["type"] = bucket_type
            df["agg"] = agg_name if agg_name is not None else sc_obj.agg
            df["group"] = group_label
            df["season_type"] = sc_obj.season_type
            df["collection"] = f"{sc_obj.mode}.{bucket_type}{('.' + df['agg'].iloc[0]) if df['agg'].notna().all() and df['agg'].iloc[0] else ''}.{group_label}"
            df_f = _apply_filters(df, filters)
            if not df_f.empty:
                flat_frames.append(df_f)

        collections = getattr(self, "collections", None)
        if not collections or mode not in collections or collections[mode] == {}:
            raise Exception(f'Collection ({mode}) needs to be built via build_collections({mode.lower()}=True)')

        mode_node = collections[mode]
        flat_frames = []

        # Walk types in a consistent order
        for type_key in ["Actual", "Average", "Expected", "Projected"]:
            if type_key not in mode_node:
                continue
            node = mode_node[type_key]

            # Two shapes exist:
            # 1) Flat: {'team': WeeklyStatCollection, 'opponent': WeeklyStatCollection}
            # 2) Nested: {agg_name: {'team': WeeklyStatCollection, 'opponent': WeeklyStatCollection}}
            # Detect by inspecting a value.
            if not node:  # empty dict
                continue

            sample_val = next(iter(node.values()))
            is_flat = hasattr(sample_val, "frame")  # WeeklyStatCollection-like
            if is_flat:
                # Flat: team/opponent directly
                _append_with_meta(node.get("team"), "team", type_key, None)
                _append_with_meta(node.get("opponent"), "opponent", type_key, None)
            else:
                # Nested by agg
                for agg_name, sides in node.items():
                    _append_with_meta(sides.get("team"), "team", type_key, agg_name)
                    _append_with_meta(sides.get("opponent"), "opponent", type_key, agg_name)

        if not flat_frames:
            return pd.DataFrame(columns=["mode", "type", "agg", "group", "season_type", "collection"])

        out = pd.concat(flat_frames, ignore_index=True, sort=False)

        # Make metadata columns prominent
        meta_cols = ["mode", "type", "agg", "group", "season_type", "collection"]
        other_cols = [c for c in out.columns if c not in meta_cols]
        return out[meta_cols + other_cols]

if __name__ == '__main__':
    pdc = WeeklyBoxscoreComponent(list(range(2023, 2026)))
    pdc.build_collections(team=False, player_group=False, player=True)
    pg_view = pdc.make_view(
        mode="Player",
        filters={"season": 2024, "week": 11, "player_id": '00-0034857'}
    )
    pg_view = pg_view
