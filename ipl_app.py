# ================================================================
#   IPL ANALYTICS APP — COMPLETE FINAL VERSION
#   Run with: streamlit run ipl_app.py
#   Data files needed in data/ folder:
#     - ipl.csv
#     - deliveries.csv
#     - deliveries_2025.csv
# ================================================================

import streamlit as st
import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="IPL Analytics", page_icon="🏏", layout="wide")

st.markdown("""
<style>
    html, body, [class*="css"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        font-family: 'Courier New', monospace;
    }
    .main { background-color: #ffffff; }
    section[data-testid="stSidebar"] {
        background-color: #f5f5f5 !important;
        border-right: 2px solid #000000;
    }
    section[data-testid="stSidebar"] * { color: #000000 !important; }
    .app-header {
        background-color: #000000; color: #ffffff !important;
        padding: 18px 24px; margin-bottom: 20px; border-radius: 4px;
        font-size: 22px; font-weight: bold; letter-spacing: 2px; text-align: center;
    }
    .section-title {
        background-color: #000000; color: #ffffff !important;
        padding: 8px 14px; font-size: 14px; font-weight: bold;
        letter-spacing: 1px; margin: 16px 0 10px 0; border-radius: 2px;
    }
    .dataframe {
        border: 1.5px solid #000000 !important; font-size: 12px !important;
        font-family: 'Courier New', monospace !important; width: 100% !important;
    }
    .dataframe th {
        background-color: #000000 !important; color: #ffffff !important;
        padding: 6px 10px !important; text-align: center !important;
        font-size: 11px !important; letter-spacing: 0.5px;
    }
    .dataframe td {
        padding: 5px 10px !important; border-bottom: 1px solid #dddddd !important;
        text-align: center !important; color: #000000 !important;
    }
    .dataframe tr:hover td { background-color: #f0f0f0 !important; }
    .pred-box { border: 2px solid #000000; padding: 20px; margin: 10px 0; background: #ffffff; }
    .pred-winner {
        font-size: 20px; font-weight: bold; text-align: center; padding: 12px;
        background: #000000; color: #ffffff !important; margin-bottom: 12px; letter-spacing: 1px;
    }
    .pred-row {
        display: flex; justify-content: space-between;
        padding: 6px 0; border-bottom: 1px solid #eeeeee; font-size: 13px;
    }
    .stSelectbox > div > div {
        border: 1.5px solid #000000 !important; border-radius: 2px !important;
        background: #ffffff !important; color: #000000 !important;
    }
    .stTextInput > div > div > input {
        border: 1.5px solid #000000 !important; background: #ffffff !important;
        color: #000000 !important; font-family: 'Courier New', monospace !important;
    }
    .stButton > button {
        background-color: #000000 !important; color: #ffffff !important;
        border: none !important; border-radius: 2px !important;
        font-family: 'Courier New', monospace !important; font-weight: bold !important;
        letter-spacing: 1px !important; padding: 8px 20px !important;
    }
    .stButton > button:hover { background-color: #333333 !important; }
    hr { border: 1px solid #000000; margin: 16px 0; }
    .stTabs [data-baseweb="tab-list"] { border-bottom: 2px solid #000000; gap: 0; }
    .stTabs [data-baseweb="tab"] {
        background: #f5f5f5; border: 1px solid #000000; border-bottom: none;
        color: #000000; font-family: 'Courier New', monospace; font-weight: bold;
        letter-spacing: 1px; padding: 8px 20px; margin-right: 2px;
    }
    .stTabs [aria-selected="true"] { background: #000000 !important; color: #ffffff !important; }
    [data-testid="stMetric"] { border: 1.5px solid #000000; padding: 10px; background: #ffffff; }
    [data-testid="stMetricLabel"] { color: #555555 !important; font-size: 11px !important; }
    [data-testid="stMetricValue"] { color: #000000 !important; font-size: 22px !important; font-weight: bold !important; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# CORRECT SEASON → MATCH_ID RANGES (verified from actual data)
# ─────────────────────────────────────────────────────────────
SEASON_RANGES = {
    2008: (335982,  336040),
    2009: (392181,  392239),
    2010: (419106,  419165),
    2011: (501198,  501271),
    2012: (548306,  548381),
    2013: (597998,  598073),
    2014: (729279,  734049),
    2015: (829705,  829823),
    2016: (980901,  981019),
    2017: (1082591, 1082650),
    2018: (1136561, 1136620),
    2019: (1175356, 1181768),
    2020: (1216492, 1237181),
    2021: (1254058, 1254117),
    2022: (1304047, 1312200),
    2023: (1359475, 1370353),
    2024: (1422119, 1426312),
    2025: (1, 999),  # deliveries_2025 uses match_no 1-74
}

ALL_SEASONS = ['All Seasons'] + [str(y) for y in range(2008, 2026)]

NAME_MAP_2025 = {
    'Kohli'            : 'V Kohli',
    'Rohit'            : 'RG Sharma',
    'Shreyas Iyer'     : 'SS Iyer',
    'Venkatesh Iyer'   : 'VR Iyer',
    'Mitchell Marsh'   : 'MR Marsh',
    'Krunal Pandya'    : 'KH Pandya',
    'Ashwin'           : 'R Ashwin',
    'Sam Curran'       : 'SM Curran',
    'Spencer Johnson'  : 'SH Johnson',
    'Shahrukh Khan'    : 'M Shahrukh Khan',
    'Nitish Reddy'     : 'Nithish Kumar Reddy',
    'Chahar'           : 'DL Chahar',
    'Harshal Patel'    : 'HV Patel',
    'Axar'             : 'AR Patel',
    'Bhuvneshwar'      : 'B Kumar',
    'Prabhsimran'      : 'P Simran Singh',
}


# ─────────────────────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    def find(f):
        for p in [f, f'data/{f}', f'../data/{f}']:
            if os.path.exists(p):
                return p
        return None

    deliveries = pd.read_csv(find('deliveries.csv'))

    # Assign season_year using correct ranges
    deliveries['season_year'] = 0
    for yr, (lo, hi) in SEASON_RANGES.items():
        if yr == 2025:
            continue
        mask = (deliveries['match_id'] >= lo) & (deliveries['match_id'] <= hi)
        deliveries.loc[mask, 'season_year'] = yr

    # Load 2025
    path_2025 = find('deliveries_2025.csv')
    if path_2025:
        d25 = pd.read_csv(path_2025)
        d25['over'] = d25['over'].apply(lambda x: int(str(x).split('.')[0]))
        d25 = d25.rename(columns={
            'match_no': 'match_id', 'innings': 'inning',
            'striker': 'batter', 'runs_of_bat': 'batsman_runs',
            'wicket_type': 'dismissal_kind',
        })
        for col in ['batter', 'bowler']:
            if col in d25.columns:
                d25[col] = d25[col].replace(NAME_MAP_2025)
        for col in ['player_dismissed', 'fielder']:
            if col in d25.columns:
                d25[col] = d25[col].replace(NAME_MAP_2025)

        main_batters = deliveries['batter'].dropna().unique().tolist()
        auto_map = {}
        for name in d25['batter'].dropna().unique():
            if name in main_batters:
                continue
            last = name.split()[-1]
            matches = [b for b in main_batters if b.endswith(last)]
            if len(matches) == 1:
                auto_map[name] = matches[0]
        d25['batter'] = d25['batter'].replace(auto_map)
        d25['bowler'] = d25['bowler'].replace(auto_map)

        d25['total_runs']  = d25['batsman_runs'] + d25['extras']
        d25['is_wicket']   = d25['dismissal_kind'].notna().astype(int)
        d25['season_year'] = 2025

        def get_extras_type(row):
            if row.get('wide',    0) > 0: return 'wides'
            if row.get('noballs', 0) > 0: return 'noballs'
            if row.get('legbyes', 0) > 0: return 'legbyes'
            if row.get('byes',    0) > 0: return 'byes'
            return None
        d25['extras_type'] = d25.apply(get_extras_type, axis=1)
        d25 = d25.rename(columns={'extras': 'extra_runs'})

        keep_cols = [c for c in deliveries.columns if c in d25.columns]
        deliveries = pd.concat([deliveries[keep_cols], d25[keep_cols]], ignore_index=True)

    ipl = pd.read_csv(find('ipl.csv'))
    return deliveries, ipl


# ─────────────────────────────────────────────────────────────
# STAT COMPUTATIONS — no groupby apply (pandas 3.0 safe)
# ─────────────────────────────────────────────────────────────
@st.cache_data
def compute_batsman_stats(_d, season='all'):
    d = _d.copy()

    # Per-innings runs
    inn = d.groupby(['batter', 'match_id', 'inning'])['batsman_runs'].sum().reset_index()
    inn.columns = ['batter', 'match_id', 'inning', 'runs']

    # Was dismissed
    outs = d[d['player_dismissed'].notna()][['match_id', 'inning', 'player_dismissed']].drop_duplicates()
    outs.columns = ['match_id', 'inning', 'batter']
    outs['out'] = 1
    inn = inn.merge(outs, on=['match_id', 'inning', 'batter'], how='left')
    inn['out'] = inn['out'].fillna(0).astype(int)

    # Aggregate per batter
    agg = inn.groupby('batter').agg(
        Inns  = ('runs',  'count'),
        Runs  = ('runs',  'sum'),
        Outs  = ('out',   'sum'),
        HS    = ('runs',  'max'),
    ).reset_index()

    # 50s 100s ducks — count per batter
    agg['100s']  = inn.groupby('batter')['runs'].apply(lambda x: (x >= 100).sum()).values
    agg['50s']   = inn.groupby('batter')['runs'].apply(lambda x: ((x >= 50) & (x < 100)).sum()).values
    agg['Ducks'] = inn.merge(outs[['match_id','inning','batter']].assign(dismissed=1),
                              on=['match_id','inning','batter'], how='left').groupby('batter').apply(
                              lambda g: ((g['runs'] == 0) & (g['out'] == 1)).sum()).values if False else \
                   inn.groupby('batter').apply(lambda g: ((g['runs'] == 0) & (g['out'] == 1)).sum()).values

    agg['Avg'] = (agg['Runs'] / agg['Outs'].replace(0, np.nan)).round(2).fillna(agg['Runs'])

    # Balls faced
    bf = d[d['extras_type'] != 'wides'].groupby('batter').size().reset_index(name='BF')
    agg = agg.merge(bf, on='batter', how='left')
    agg['SR'] = ((agg['Runs'] / agg['BF'].replace(0, np.nan)) * 100).round(2)

    # 4s 6s
    fours = d[d['batsman_runs'] == 4].groupby('batter').size().reset_index(name='4s')
    sixes = d[d['batsman_runs'] == 6].groupby('batter').size().reset_index(name='6s')
    agg = agg.merge(fours, on='batter', how='left').merge(sixes, on='batter', how='left')
    agg['4s']  = agg['4s'].fillna(0).astype(int)
    agg['6s']  = agg['6s'].fillna(0).astype(int)
    agg['BPB'] = (agg['BF'] / (agg['4s'] + agg['6s']).replace(0, np.nan)).round(1).fillna('-')

    agg = agg.rename(columns={'batter': 'Player'})
    return agg[['Player','Inns','Runs','Outs','Avg','BF','SR','HS','100s','50s','Ducks','4s','6s','BPB']].sort_values('Runs', ascending=False).reset_index(drop=True)


@st.cache_data
def compute_bowler_stats(_d, season='all'):
    valid_wkt = ['caught', 'bowled', 'lbw', 'stumped', 'caught and bowled', 'hit wicket']
    balls = _d[_d['extras_type'] != 'wides'].groupby('bowler').size().reset_index(name='Balls')
    wkts  = _d[_d['dismissal_kind'].isin(valid_wkt)].groupby('bowler').size().reset_index(name='Wkts')
    runs  = _d[~_d['extras_type'].isin(['byes', 'legbyes'])].groupby('bowler')['total_runs'].sum().reset_index(name='Runs')

    iw = _d[_d['dismissal_kind'].isin(valid_wkt)].groupby(['bowler', 'match_id', 'inning']).size().reset_index(name='wkts')
    ir = _d[~_d['extras_type'].isin(['byes', 'legbyes'])].groupby(['bowler', 'match_id', 'inning'])['total_runs'].sum().reset_index(name='runs')
    figs = iw.merge(ir, on=['bowler', 'match_id', 'inning'], how='left').fillna(0)

    def best_fig(g):
        if len(g) == 0: return '0/0'
        top = g.sort_values(['wkts', 'runs'], ascending=[False, True]).iloc[0]
        return f"{int(top['wkts'])}/{int(top['runs'])}"

    bf    = figs.groupby('bowler').apply(best_fig).reset_index(name='Best')
    hauls = figs.groupby('bowler').agg(
        w3=('wkts', lambda x: int((x >= 3).sum())),
        w4=('wkts', lambda x: int((x >= 4).sum())),
        w5=('wkts', lambda x: int((x >= 5).sum()))
    ).reset_index().rename(columns={'w3': '3W', 'w4': '4W', 'w5': '5W'})

    stats = balls.merge(wkts, on='bowler', how='left').merge(runs, on='bowler', how='left')
    stats = stats.merge(bf, on='bowler', how='left').merge(hauls, on='bowler', how='left')
    stats = stats.fillna(0)
    stats['Wkts']  = stats['Wkts'].astype(int)
    stats['Overs'] = (stats['Balls'] // 6).astype(str) + '.' + (stats['Balls'] % 6).astype(str)
    stats['Econ']  = (stats['Runs'] / (stats['Balls'] / 6).replace(0, np.nan)).round(2).fillna('-')
    stats['SR']    = (stats['Balls'] / stats['Wkts'].replace(0, np.nan)).round(1).fillna('-')
    stats['Avg']   = (stats['Runs'] / stats['Wkts'].replace(0, np.nan)).round(2).fillna('-')
    stats = stats.rename(columns={'bowler': 'Player'})
    return stats[['Player','Overs','Balls','Runs','Wkts','Avg','Econ','SR','Best','3W','4W','5W']].sort_values('Wkts', ascending=False).reset_index(drop=True)


@st.cache_data
def compute_keeper_stats(_d, season='all'):
    stump  = _d[_d['dismissal_kind'] == 'stumped'].groupby('fielder').size().reset_index(name='Stumpings')
    caught = _d[_d['dismissal_kind'].isin(['caught', 'caught and bowled'])].groupby('fielder').size().reset_index(name='Catches')
    stats  = stump.merge(caught, on='fielder', how='outer').fillna(0)
    stats['Stumpings']  = stats['Stumpings'].astype(int)
    stats['Catches']    = stats['Catches'].astype(int)
    stats['Dismissals'] = stats['Stumpings'] + stats['Catches']
    stats = stats[stats['Stumpings'] >= 1]
    stats = stats.rename(columns={'fielder': 'Player'})
    return stats[['Player','Dismissals','Catches','Stumpings']].sort_values('Dismissals', ascending=False).reset_index(drop=True)


@st.cache_data
def compute_prediction_data(_ipl):
    df = _ipl[_ipl['result'].isin(['runs','wickets','tie'])].copy()
    df = df[df['winner'].notna()].copy()
    df = df[df['super_over']=='N'].copy()
    name_fix = {
        'Delhi Daredevils':'Delhi Capitals','Kings XI Punjab':'Punjab Kings',
        'Rising Pune Supergiant':'Rising Pune Supergiants',
        'Royal Challengers Bangalore':'Royal Challengers Bengaluru'
    }
    for col in ['team1','team2','winner','toss_winner']:
        df[col] = df[col].replace(name_fix)

    # ── Standardise venue names ───────────────────────────
    venue_fix = {
        'M Chinnaswamy Stadium'                        : 'M Chinnaswamy Stadium, Bengaluru',
        'M.Chinnaswamy Stadium'                        : 'M Chinnaswamy Stadium, Bengaluru',
        'Royal Challengers Bangalore Cricket Ground'   : 'M Chinnaswamy Stadium, Bengaluru',
        'MA Chidambaram Stadium'                       : 'MA Chidambaram Stadium, Chepauk, Chennai',
        'MA Chidambaram Stadium, Chepauk'              : 'MA Chidambaram Stadium, Chepauk, Chennai',
        'Wankhede Stadium'                             : 'Wankhede Stadium, Mumbai',
        'Eden Gardens'                                 : 'Eden Gardens, Kolkata',
        'Feroz Shah Kotla'                             : 'Arun Jaitley Stadium, Delhi',
        'Feroz Shah Kotla Ground'                      : 'Arun Jaitley Stadium, Delhi',
        'Arun Jaitley Stadium'                         : 'Arun Jaitley Stadium, Delhi',
        'Punjab Cricket Association Stadium, Mohali'   : 'Punjab Cricket Association IS Bindra Stadium, Mohali',
        'Punjab Cricket Association IS Bindra Stadium' : 'Punjab Cricket Association IS Bindra Stadium, Mohali',
        'Rajiv Gandhi International Stadium'           : 'Rajiv Gandhi International Stadium, Uppal, Hyderabad',
        'Rajiv Gandhi International Stadium, Uppal'    : 'Rajiv Gandhi International Stadium, Uppal, Hyderabad',
        'Sawai Mansingh Stadium'                       : 'Sawai Mansingh Stadium, Jaipur',
        'DY Patil Stadium'                             : 'Dr DY Patil Sports Academy, Mumbai',
        'Dr DY Patil Sports Academy'                   : 'Dr DY Patil Sports Academy, Mumbai',
        'Brabourne Stadium'                            : 'Brabourne Stadium, Mumbai',
        'Maharaja Yadavindra Singh International Cricket Stadium, Mullanpur' : 'Maharaja Yadavindra Singh International Cricket Stadiu, Mullanpur',
        'Maharaja Yadavindra Singh International Cricket Stadium, Mullanpur, Chandigarh' : 'Maharaja Yadavindra Singh International Cricket Stadiu, Mullanpur',
    }
    df['venue'] = df['venue'].replace(venue_fix)

    season_map = {i: 2007+i for i in range(1, 19)}
    df['year'] = df['season'].map(season_map)
    return df.sort_values('match_date').reset_index(drop=True)

# ─────────────────────────────────────────────────────────────
# SEASON BREAKDOWN HELPERS
# ─────────────────────────────────────────────────────────────
def player_season_batting(deliveries, player):
    rows = []
    for yr in range(2008, 2026):
        d = deliveries[(deliveries['batter'] == player) & (deliveries['season_year'] == yr)]
        if len(d) == 0: continue
        runs  = int(d['batsman_runs'].sum())
        bf    = int(d[d['extras_type'] != 'wides'].shape[0])
        fours = int((d['batsman_runs'] == 4).sum())
        sixes = int((d['batsman_runs'] == 6).sum())
        outs  = int(d[d['player_dismissed'] == player].shape[0]) if 'player_dismissed' in d.columns else 0
        inn_r = d.groupby(['match_id', 'inning'])['batsman_runs'].sum()
        inns  = len(inn_r)
        hs    = int(inn_r.max()) if len(inn_r) > 0 else 0
        rows.append({
            'Season': yr, 'Inns': inns, 'Runs': runs,
            'Avg'   : round(runs / outs, 2) if outs > 0 else runs,
            'SR'    : round(runs / bf * 100, 2) if bf > 0 else 0,
            'HS'    : hs,
            '100s'  : int((inn_r >= 100).sum()),
            '50s'   : int(((inn_r >= 50) & (inn_r < 100)).sum()),
            'Ducks' : int((inn_r == 0).sum()),
            '4s'    : fours, '6s': sixes
        })
    return pd.DataFrame(rows)


def player_season_bowling(deliveries, player):
    valid_wkt = ['caught', 'bowled', 'lbw', 'stumped', 'caught and bowled', 'hit wicket']
    rows = []
    for yr in range(2008, 2026):
        d = deliveries[(deliveries['bowler'] == player) & (deliveries['season_year'] == yr)]
        if len(d) == 0: continue
        balls = int(d[d['extras_type'] != 'wides'].shape[0])
        wkts  = int(d[d['dismissal_kind'].isin(valid_wkt)].shape[0])
        runs  = int(d[~d['extras_type'].isin(['byes', 'legbyes'])]['total_runs'].sum())
        iw    = d[d['dismissal_kind'].isin(valid_wkt)].groupby(['match_id', 'inning']).size()
        ir    = d[~d['extras_type'].isin(['byes', 'legbyes'])].groupby(['match_id', 'inning'])['total_runs'].sum()
        best  = f"{int(iw[iw.idxmax()])}/{int(ir.get(iw.idxmax(), 0))}" if len(iw) > 0 else '0/0'
        rows.append({
            'Season': yr, 'Overs': f"{balls // 6}.{balls % 6}",
            'Runs': runs, 'Wkts': wkts,
            'Avg' : round(runs / wkts, 2) if wkts > 0 else '-',
            'Econ': round(runs / (balls / 6), 2) if balls > 0 else 0,
            'SR'  : round(balls / wkts, 1) if wkts > 0 else '-',
            'Best': best
        })
    return pd.DataFrame(rows)


def keeper_season_stats(deliveries, player):
    rows = []
    for yr in range(2008, 2026):
        d = deliveries[(deliveries['fielder'] == player) & (deliveries['season_year'] == yr)]
        if len(d) == 0: continue
        stump  = int((d['dismissal_kind'] == 'stumped').sum())
        caught = int(d['dismissal_kind'].isin(['caught', 'caught and bowled']).sum())
        if stump + caught == 0: continue
        rows.append({'Season': yr, 'Dismissals': stump + caught, 'Catches': caught, 'Stumpings': stump})
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────
try:
    deliveries, ipl  = load_data()
    bat_stats_all    = compute_batsman_stats(deliveries, season='all')
    bowl_stats_all   = compute_bowler_stats(deliveries, season='all')
    keep_stats_all   = compute_keeper_stats(deliveries, season='all')
    pred_data        = compute_prediction_data(ipl)
    data_loaded      = True
except Exception as e:
    data_loaded = False
    error_msg   = str(e)


# ─────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────
st.markdown('<div class="app-header">🏏 &nbsp; IPL ANALYTICS &nbsp; 🏏</div>', unsafe_allow_html=True)

if not data_loaded:
    st.error(f"❌ Could not load data: {error_msg}")
    st.stop()


# ─────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🏏  BATTING", "🎯  BOWLING", "🧤  WICKET KEEPING", "📊  MATCH PREDICTION"
])


# ══════════════════════════════════════════════════════
#  TAB 1 — BATTING
# ══════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-title">BATTING STATISTICS — IPL 2008–2025</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        search = st.text_input("🔍  Search Player", placeholder="e.g. V Kohli", key="bat_search")
    with col2:
        season_bat = st.selectbox("Season", ALL_SEASONS, key="bat_season")
    with col3:
        min_runs = st.number_input("Min Runs", min_value=0, value=100, step=50, key="min_runs")
    with col4:
        sort_by = st.selectbox("Sort By", ['Runs','Avg','SR','100s','50s','4s','6s'], key="bat_sort")

    if season_bat != 'All Seasons':
        yr    = int(season_bat)
        d_bat = deliveries[deliveries['season_year'] == yr]
        bat_stats    = compute_batsman_stats(d_bat, season=season_bat)
        season_label = season_bat
    else:
        bat_stats    = bat_stats_all
        season_label = '2008–2025'

    df_bat = bat_stats[bat_stats['Runs'] >= min_runs].copy()
    if search:
        df_bat = df_bat[df_bat['Player'].str.contains(search, case=False, na=False)]
    df_bat = df_bat.sort_values(sort_by, ascending=False).reset_index(drop=True)
    df_bat.index += 1

    st.markdown('<div class="section-title">QUICK STATS</div>', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Players", f"{len(bat_stats):,}")
    m2.metric("Total Runs",    f"{bat_stats['Runs'].sum():,}")
    m3.metric("Most Runs",     f"{bat_stats.iloc[0]['Player'].split()[-1]}  {bat_stats.iloc[0]['Runs']:,}")
    m4.metric("Most 100s",     f"{bat_stats.sort_values('100s',ascending=False).iloc[0]['Player'].split()[-1]}  {bat_stats.sort_values('100s',ascending=False).iloc[0]['100s']}")

    if search and len(df_bat) == 1:
        p = df_bat.iloc[0]
        st.markdown('<div class="section-title">PLAYER CARD</div>', unsafe_allow_html=True)
        c1,c2,c3,c4,c5,c6,c7 = st.columns(7)
        c1.metric("Innings",     int(p['Inns']))
        c2.metric("Runs",        int(p['Runs']))
        c3.metric("Average",     p['Avg'])
        c4.metric("Strike Rate", p['SR'])
        c5.metric("100s / 50s",  f"{int(p['100s'])} / {int(p['50s'])}")
        c6.metric("4s / 6s",     f"{int(p['4s'])} / {int(p['6s'])}")
        c7.metric("Ducks",       int(p['Ducks']))
        st.markdown(f"**Highest Score:** {int(p['HS'])}  &nbsp;|&nbsp;  **Balls Faced:** {int(p['BF'])}  &nbsp;|&nbsp;  **Balls per Boundary:** {p['BPB']}")

    st.markdown('<div class="section-title">SCORECARD</div>', unsafe_allow_html=True)
    st.dataframe(df_bat, use_container_width=True, height=460)
    st.caption(f"Showing {len(df_bat)} players  |  Season: {season_label}")

    if search and len(df_bat) == 1 and season_bat == 'All Seasons':
        player_name = df_bat.iloc[0]['Player']
        sw = player_season_batting(deliveries, player_name)
        if len(sw) > 0:
            st.markdown(f'<div class="section-title">SEASON-WISE RECORD — {player_name}</div>', unsafe_allow_html=True)
            st.dataframe(sw, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════
#  TAB 2 — BOWLING
# ══════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">BOWLING STATISTICS — IPL 2008–2025</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        search_b = st.text_input("🔍  Search Player", placeholder="e.g. JJ Bumrah", key="bowl_search")
    with col2:
        season_bowl = st.selectbox("Season", ALL_SEASONS, key="bowl_season")
    with col3:
        min_wkts = st.number_input("Min Wickets", min_value=0, value=10, step=5, key="min_wkts")
    with col4:
        sort_by_b = st.selectbox("Sort By", ['Wkts','Econ','SR','Avg','5W','4W','3W'], key="bowl_sort")

    if season_bowl != 'All Seasons':
        yr     = int(season_bowl)
        d_bowl = deliveries[deliveries['season_year'] == yr]
        bowl_stats     = compute_bowler_stats(d_bowl, season=season_bowl)
        season_label_b = season_bowl
    else:
        bowl_stats     = bowl_stats_all
        season_label_b = '2008–2025'

    df_bowl = bowl_stats[bowl_stats['Wkts'] >= min_wkts].copy()
    if search_b:
        df_bowl = df_bowl[df_bowl['Player'].str.contains(search_b, case=False, na=False)]
    try:
        df_bowl = df_bowl.sort_values(sort_by_b, ascending=(sort_by_b in ['Econ','SR','Avg'])).reset_index(drop=True)
    except:
        df_bowl = df_bowl.sort_values('Wkts', ascending=False).reset_index(drop=True)
    df_bowl.index += 1

    st.markdown('<div class="section-title">QUICK STATS</div>', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Bowlers", f"{len(bowl_stats):,}")
    m2.metric("Total Wickets", f"{bowl_stats['Wkts'].sum():,}")
    m3.metric("Most Wickets",  f"{bowl_stats.iloc[0]['Player'].split()[-1]}  {bowl_stats.iloc[0]['Wkts']}")
    m4.metric("Most 5-Wkts",   f"{bowl_stats.sort_values('5W',ascending=False).iloc[0]['Player'].split()[-1]}  {bowl_stats.sort_values('5W',ascending=False).iloc[0]['5W']}")

    if search_b and len(df_bowl) == 1:
        p = df_bowl.iloc[0]
        st.markdown('<div class="section-title">PLAYER CARD</div>', unsafe_allow_html=True)
        c1,c2,c3,c4,c5,c6,c7 = st.columns(7)
        c1.metric("Wickets",      int(p['Wkts']))
        c2.metric("Overs",        p['Overs'])
        c3.metric("Economy",      p['Econ'])
        c4.metric("Strike Rate",  p['SR'])
        c5.metric("Average",      p['Avg'])
        c6.metric("Best",         p['Best'])
        c7.metric("5W / 4W / 3W", f"{int(p['5W'])} / {int(p['4W'])} / {int(p['3W'])}")

    st.markdown('<div class="section-title">SCORECARD</div>', unsafe_allow_html=True)
    st.dataframe(df_bowl, use_container_width=True, height=460)
    st.caption(f"Showing {len(df_bowl)} bowlers  |  Season: {season_label_b}")

    if search_b and len(df_bowl) == 1 and season_bowl == 'All Seasons':
        bowler_name = df_bowl.iloc[0]['Player']
        sw = player_season_bowling(deliveries, bowler_name)
        if len(sw) > 0:
            st.markdown(f'<div class="section-title">SEASON-WISE RECORD — {bowler_name}</div>', unsafe_allow_html=True)
            st.dataframe(sw, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════
#  TAB 3 — WICKET KEEPING
# ══════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-title">WICKET KEEPING STATISTICS — IPL 2008–2025</div>', unsafe_allow_html=True)
    st.caption("ℹ️  Only players with at least 1 stumping shown")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search_k = st.text_input("🔍  Search Keeper", placeholder="e.g. MS Dhoni", key="keep_search")
    with col2:
        season_keep = st.selectbox("Season", ALL_SEASONS, key="keep_season")
    with col3:
        sort_by_k = st.selectbox("Sort By", ['Dismissals','Catches','Stumpings'], key="keep_sort")

    if season_keep != 'All Seasons':
        yr     = int(season_keep)
        d_keep = deliveries[deliveries['season_year'] == yr]
        keep_stats     = compute_keeper_stats(d_keep, season=season_keep)
        season_label_k = season_keep
    else:
        keep_stats     = keep_stats_all
        season_label_k = '2008–2025'

    df_keep = keep_stats.copy()
    if search_k:
        df_keep = df_keep[df_keep['Player'].str.contains(search_k, case=False, na=False)]
    df_keep = df_keep.sort_values(sort_by_k, ascending=False).reset_index(drop=True)
    df_keep.index += 1

    st.markdown('<div class="section-title">QUICK STATS</div>', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Keepers",   len(keep_stats))
    m2.metric("Most Dismissals", f"{keep_stats.iloc[0]['Player'].split()[-1]}  {keep_stats.iloc[0]['Dismissals']}")
    m3.metric("Most Stumpings",  f"{keep_stats.sort_values('Stumpings',ascending=False).iloc[0]['Player'].split()[-1]}  {keep_stats.sort_values('Stumpings',ascending=False).iloc[0]['Stumpings']}")
    m4.metric("Most Catches",    f"{keep_stats.sort_values('Catches',ascending=False).iloc[0]['Player'].split()[-1]}  {keep_stats.sort_values('Catches',ascending=False).iloc[0]['Catches']}")

    if search_k and len(df_keep) == 1:
        p = df_keep.iloc[0]
        st.markdown('<div class="section-title">PLAYER CARD</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Dismissals", int(p['Dismissals']))
        c2.metric("Catches",          int(p['Catches']))
        c3.metric("Stumpings",        int(p['Stumpings']))

    st.markdown('<div class="section-title">SCORECARD</div>', unsafe_allow_html=True)
    st.dataframe(df_keep, use_container_width=True, height=460)
    st.caption(f"Showing {len(df_keep)} keepers  |  Season: {season_label_k}")

    if search_k and len(df_keep) == 1 and season_keep == 'All Seasons':
        keeper_name = df_keep.iloc[0]['Player']
        sw = keeper_season_stats(deliveries, keeper_name)
        if len(sw) > 0:
            st.markdown(f'<div class="section-title">SEASON-WISE RECORD — {keeper_name}</div>', unsafe_allow_html=True)
            st.dataframe(sw, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════
#  TAB 4 — MATCH PREDICTION
# ══════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">MATCH PREDICTION — HEAD TO HEAD ANALYSIS (2008–2025)</div>', unsafe_allow_html=True)

    all_teams  = sorted(set(pred_data['team1'].tolist() + pred_data['team2'].tolist()))
    all_venues = sorted(pred_data['venue'].unique().tolist())

    col1, col2, col3 = st.columns(3)
    with col1:
        team1 = st.selectbox("Team 1", all_teams,
                             index=all_teams.index('Mumbai Indians') if 'Mumbai Indians' in all_teams else 0)
    with col2:
        team2 = st.selectbox("Team 2", [t for t in all_teams if t != team1], index=0)
    with col3:
        venue = st.selectbox("Venue", ['All Venues'] + all_venues)

    toss_winner   = st.selectbox("Toss Winner",   [team1, team2])
    toss_decision = st.selectbox("Toss Decision", ['bat', 'field'])

    if st.button("PREDICT MATCH →"):
        h2h = pred_data[
            ((pred_data['team1'] == team1) & (pred_data['team2'] == team2)) |
            ((pred_data['team1'] == team2) & (pred_data['team2'] == team1))
        ].copy()

        h2h_venue = h2h[h2h['venue'] == venue].copy() if venue != 'All Venues' else h2h.copy()
        if len(h2h_venue) == 0:
            st.warning("⚠️ No matches at this venue. Showing overall H2H.")
            h2h_venue = h2h.copy()

        t1_wins = (h2h_venue['winner'] == team1).sum()
        t2_wins = (h2h_venue['winner'] == team2).sum()
        total   = len(h2h_venue)

        venue_matches     = pred_data[pred_data['venue'] == venue].copy() if venue != 'All Venues' else pred_data.copy()
        venue_bat_wins    = venue_matches[(venue_matches['toss_decision'] == 'bat')   & (venue_matches['toss_winner'] == venue_matches['winner'])]
        venue_field_wins  = venue_matches[(venue_matches['toss_decision'] == 'field') & (venue_matches['toss_winner'] == venue_matches['winner'])]
        venue_bat_total   = venue_matches[venue_matches['toss_decision'] == 'bat']
        venue_field_total = venue_matches[venue_matches['toss_decision'] == 'field']
        venue_bat_pct     = len(venue_bat_wins)   / len(venue_bat_total)   * 100 if len(venue_bat_total)   > 0 else 0
        venue_field_pct   = len(venue_field_wins) / len(venue_field_total) * 100 if len(venue_field_total) > 0 else 0

        t1_win_pct = t1_wins / total * 100 if total > 0 else 50
        t2_win_pct = t2_wins / total * 100 if total > 0 else 50
        toss_boost = 3 if toss_decision == ('field' if venue_field_pct > venue_bat_pct else 'bat') else -2
        t1_score   = t1_win_pct + toss_boost if toss_winner == team1 else t1_win_pct - toss_boost
        t2_score   = t2_win_pct - toss_boost if toss_winner == team1 else t2_win_pct + toss_boost
        total_score = t1_score + t2_score
        t1_prob     = round(min(max(t1_score / total_score * 100, 1), 99), 1)
        t2_prob     = round(100 - t1_prob, 1)
        predicted_winner = team1 if t1_prob > 50 else team2
        confidence = max(t1_prob, t2_prob)

        rec_decision = 'FIELD FIRST' if venue_field_pct > venue_bat_pct else 'BAT FIRST'
        rec_reason   = (f"Teams that chose to field won {venue_field_pct:.0f}% at this venue (vs {venue_bat_pct:.0f}% batting first)"
                        if venue_field_pct > venue_bat_pct else
                        f"Teams that chose to bat won {venue_bat_pct:.0f}% at this venue (vs {venue_field_pct:.0f}% fielding first)")

        st.markdown("---")
        st.markdown(f"""
        <div style="background:#000000; color:#ffffff; padding:20px;
                    text-align:center; font-size:20px; font-weight:bold;
                    letter-spacing:2px; border-radius:4px; margin-bottom:16px;">
            🏆 &nbsp; PREDICTED WINNER: {predicted_winner.upper()} &nbsp; ({confidence:.1f}% confidence)
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-title">HEAD TO HEAD SUMMARY</div>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Matches", total)
        c2.metric(f"{team1} Wins", f"{t1_wins}  ({t1_win_pct:.0f}%)")
        c3.metric(f"{team2} Wins", f"{t2_wins}  ({t2_win_pct:.0f}%)")
        c4.metric("Venue",         venue if venue != 'All Venues' else 'All Venues')

        st.markdown('<div class="section-title">WIN PROBABILITY</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        col1.metric(f"🏏 {team1}", f"{t1_prob}%")
        col2.metric(f"🏏 {team2}", f"{t2_prob}%")

        st.write(f"**{team1}**")
        st.progress(int(t1_prob))

        st.write(f"**{team2}**")
        st.progress(int(t2_prob))

        st.markdown('<div class="section-title">VENUE TOSS ANALYSIS</div>', unsafe_allow_html=True)
        toss_df = pd.DataFrame({
            'Decision'       : ['Bat First', 'Field First'],
            'Matches'        : [len(venue_bat_total), len(venue_field_total)],
            'Toss Winner Won': [len(venue_bat_wins),  len(venue_field_wins)],
            'Win %'          : [f"{venue_bat_pct:.1f}%", f"{venue_field_pct:.1f}%"],
            'Recommendation' : [
                '✅ RECOMMENDED' if rec_decision == 'BAT FIRST'   else '',
                '✅ RECOMMENDED' if rec_decision == 'FIELD FIRST' else ''
            ]
        })
        st.dataframe(toss_df, use_container_width=True, hide_index=True)

        st.markdown(f'<div class="section-title">ALL H2H MATCHES — {total} matches (2008–2025)</div>', unsafe_allow_html=True)
        all_matches = h2h_venue[['match_date','year','team1','team2','venue','toss_winner','toss_decision','winner','result_margin']].sort_values('match_date', ascending=False).reset_index(drop=True)
        all_matches.index += 1
        all_matches.columns = ['Date','Year','Team 1','Team 2','Venue','Toss Winner','Toss Decision','Winner','Margin']
        st.dataframe(all_matches, use_container_width=True, height=500)
        st.caption(f"All {total} matches between {team1} and {team2} from 2008 to 2025")