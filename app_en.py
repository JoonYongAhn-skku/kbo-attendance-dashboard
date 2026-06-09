"""
KBO Attendance Dashboard (English Version)
Yearly attendance trends across KBO teams with future predictions.

Author: [Your Name]
Course: Arts and Big Data — SKKU
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from pathlib import Path

# ---------- Page Configuration ----------
st.set_page_config(
    page_title="KBO Attendance Dashboard",
    page_icon="⚾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- Custom CSS ----------
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1F3864;
        margin-bottom: 0;
    }
    .subtitle {
        font-size: 1rem;
        color: #595959;
        margin-top: 0;
        margin-bottom: 1.5rem;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.6rem;
    }
</style>
""", unsafe_allow_html=True)

# ---------- Team Colors ----------
TEAM_COLORS = {
    'LG': '#C30452',
    'Doosan': '#131230',
    'KIA': '#EA0029',
    'Samsung': '#074CA1',
    'Lotte': '#041E42',
    'SSG': '#CE0E2D',
    'Hanwha': '#FF6600',
    'KT': '#000000',
    'NC': '#315288',
    'Kiwoom': '#820024',
}

# ---------- Full Team Names ----------
TEAM_FULL_NAMES = {
    'LG': 'LG Twins',
    'Doosan': 'Doosan Bears',
    'KIA': 'KIA Tigers',
    'Samsung': 'Samsung Lions',
    'Lotte': 'Lotte Giants',
    'SSG': 'SSG Landers',
    'Hanwha': 'Hanwha Eagles',
    'KT': 'KT Wiz',
    'NC': 'NC Dinos',
    'Kiwoom': 'Kiwoom Heroes',
}

# ---------- Data Loading ----------
@st.cache_data
def load_data():
    """Load KBO attendance data from CSV."""
    csv_path = Path(__file__).parent / "kbo_attendance.csv"
    df = pd.read_csv(csv_path)

    # Defensive normalization: same franchise, different sponsor names
    # Nexen Heroes (2008-2018) → Kiwoom Heroes (2019-)
    # SK Wyverns (2000-2020) → SSG Landers (2021-)
    df['team'] = df['team'].replace({'Nexen': 'Kiwoom', 'SK': 'SSG'})

    # Add per-game average
    df['avg_per_game'] = (df['attendance'] / df['games']).round(0).astype(int)
    return df

df = load_data()

# ---------- Header ----------
st.markdown('<p class="main-title">⚾ KBO Attendance Dashboard</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Yearly attendance trends across KBO teams with future predictions</p>',
    unsafe_allow_html=True
)

# ---------- Sidebar ----------
st.sidebar.header("⚙️ Filter Settings")

# Team selection
all_teams = sorted(df['team'].unique().tolist())

st.sidebar.subheader("Team Selection")
select_all = st.sidebar.checkbox("Select all teams", value=False)

if select_all:
    selected_teams = all_teams
else:
    selected_teams = st.sidebar.multiselect(
        "Choose teams to compare",
        options=all_teams,
        default=['LG', 'Doosan', 'KIA', 'Lotte'],
        format_func=lambda x: f"{x} ({TEAM_FULL_NAMES.get(x, x)})"
    )

# Year range
st.sidebar.subheader("Year Range")
min_year, max_year = int(df['year'].min()), int(df['year'].max())
year_range = st.sidebar.slider(
    "Analysis period",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
    step=1
)

# COVID exclusion (applies to chart, prediction, and insights)
exclude_covid = st.sidebar.checkbox(
    "🦠 Exclude COVID years (2020-2021)",
    value=False,
    help="2020-2021 saw abnormally low attendance due to COVID-19. "
         "When checked, these years are excluded from the chart, prediction, and insights."
)

# Prediction settings
st.sidebar.divider()
st.sidebar.subheader("🔮 Future Prediction")
enable_prediction = st.sidebar.toggle("Enable prediction", value=False)

prediction_years = 3
if enable_prediction:
    prediction_years = st.sidebar.slider(
        "Years ahead",
        min_value=1, max_value=5, value=3,
        help="How many years into the future to predict."
    )

# Info box
st.sidebar.divider()
st.sidebar.caption(
    "📊 **Data Source**\n\n"
    "KBO Official Records (koreabaseball.com)"
)

# ---------- Stop if no team selected ----------
if not selected_teams:
    st.warning("⚠️ Please select at least one team from the sidebar.")
    st.stop()

# ---------- Filter Data ----------
filtered = df[
    (df['team'].isin(selected_teams)) &
    (df['year'] >= year_range[0]) &
    (df['year'] <= year_range[1])
].copy()

# Apply COVID exclusion if checked
if exclude_covid:
    filtered = filtered[~filtered['year'].isin([2020, 2021])]

# ---------- KPI Metrics ----------
col1, col2, col3, col4 = st.columns(4)
with col1:
    total_attendance = int(filtered['attendance'].sum())
    st.metric("Total Attendance", f"{total_attendance:,}")
with col2:
    avg_per_game = int(filtered['avg_per_game'].mean())
    st.metric("Avg. per Game", f"{avg_per_game:,}")
with col3:
    st.metric("Teams Selected", f"{len(selected_teams)}")
with col4:
    span = year_range[1] - year_range[0] + 1
    if exclude_covid:
        span = span - 2 if year_range[0] <= 2020 and year_range[1] >= 2021 else span
    st.metric("Years Analyzed", f"{span}")

st.divider()

# ---------- Main Chart: Line Chart with Predictions ----------
st.subheader("📈 Yearly Attendance Trends")

fig = go.Figure()

prediction_summary = []

for team in selected_teams:
    team_data = filtered[filtered['team'] == team].sort_values('year')
    if team_data.empty:
        continue

    color = TEAM_COLORS.get(team, '#888888')

    # Actual data line
    fig.add_trace(go.Scatter(
        x=team_data['year'],
        y=team_data['attendance'],
        mode='lines+markers',
        name=team,
        line=dict(color=color, width=3),
        marker=dict(size=9),
        hovertemplate=f"<b>{team}</b><br>%{{x}}: %{{y:,}}<extra></extra>"
    ))

    # Prediction
    if enable_prediction:
        # team_data is already COVID-filtered upstream if user checked the box
        train_data = team_data.copy()

        if len(train_data) >= 3:
            X = train_data['year'].values.reshape(-1, 1)
            y = train_data['attendance'].values

            model = LinearRegression()
            model.fit(X, y)

            last_year = int(team_data['year'].max())
            last_value = int(team_data[team_data['year'] == last_year]['attendance'].values[0])

            future_years_arr = np.arange(last_year + 1, last_year + 1 + prediction_years)
            future_X = future_years_arr.reshape(-1, 1)
            predictions = model.predict(future_X)
            predictions = np.clip(predictions, 0, None)  # No negative attendance

            # Connect from last actual point
            x_pred = [last_year] + future_years_arr.tolist()
            y_pred = [last_value] + predictions.tolist()

            fig.add_trace(go.Scatter(
                x=x_pred,
                y=y_pred,
                mode='lines+markers',
                name=f'{team} (predicted)',
                line=dict(color=color, width=2, dash='dash'),
                marker=dict(size=8, symbol='diamond-open'),
                hovertemplate=f"<b>{team} predicted</b><br>%{{x}}: %{{y:,.0f}}<extra></extra>"
            ))

            # Record for summary
            prediction_summary.append({
                'Team': team,
                f'{last_year} (Actual)': f"{last_value:,}",
                f'{future_years_arr[-1]} (Predicted)': f"{int(predictions[-1]):,}",
                'Annual Change': f"{int(model.coef_[0]):+,}/year",
                'R²': f"{model.score(X, y):.3f}"
            })

fig.update_layout(
    xaxis_title="Year",
    yaxis_title="Attendance",
    hovermode='x unified',
    template='plotly_white',
    height=520,
    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
)
fig.update_yaxes(tickformat=',')

st.plotly_chart(fig, use_container_width=True)

# ---------- Prediction Summary Table ----------
if enable_prediction and prediction_summary:
    st.subheader("🔮 Prediction Summary")
    pred_df = pd.DataFrame(prediction_summary)
    st.dataframe(pred_df, use_container_width=True, hide_index=True)
    st.caption(
        "💡 **R² interpretation**: closer to 1 means the linear model fits the data better. "
        "Values above 0.7 indicate fairly reliable predictions."
    )

st.divider()

# ---------- Side-by-side: Bar Chart + Table ----------
col_left, col_right = st.columns([1.3, 1])

with col_left:
    st.subheader("📊 Team Comparison by Year")
    bar_year = st.selectbox(
        "Select year",
        options=sorted(filtered['year'].unique(), reverse=True),
        index=0
    )
    bar_data = filtered[filtered['year'] == bar_year].sort_values('attendance', ascending=True)

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        y=bar_data['team'],
        x=bar_data['attendance'],
        orientation='h',
        marker_color=[TEAM_COLORS.get(t, '#888888') for t in bar_data['team']],
        text=bar_data['attendance'].apply(lambda x: f"{x:,}"),
        textposition='outside',
        hovertemplate="<b>%{y}</b><br>%{x:,}<extra></extra>"
    ))
    fig_bar.update_layout(
        xaxis_title=f"{bar_year} Attendance",
        yaxis_title="",
        template='plotly_white',
        height=420,
        showlegend=False,
        margin=dict(l=0, r=80, t=20, b=0)
    )
    fig_bar.update_xaxes(tickformat=',')
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.subheader("📋 Detailed Data")
    display_df = filtered[['year', 'team', 'stadium', 'attendance', 'avg_per_game']].copy()
    display_df.insert(2, 'full_name', display_df['team'].map(TEAM_FULL_NAMES))
    display_df.columns = ['Year', 'Team', 'Full Name', 'Stadium', 'Total', 'Avg/Game']
    display_df['Total'] = display_df['Total'].apply(lambda x: f"{x:,}")
    display_df['Avg/Game'] = display_df['Avg/Game'].apply(lambda x: f"{x:,}")
    st.dataframe(
        display_df.sort_values(['Year', 'Team'], ascending=[False, True]),
        use_container_width=True,
        hide_index=True,
        height=420
    )

# ---------- Insights ----------
st.divider()
st.subheader("💡 Key Insights")

# Compute growth between first and last year for each team
latest_year = filtered['year'].max()
earliest_year = filtered['year'].min()
insights = []

for team in selected_teams:
    early = filtered[(filtered['team'] == team) & (filtered['year'] == earliest_year)]
    late = filtered[(filtered['team'] == team) & (filtered['year'] == latest_year)]
    if not early.empty and not late.empty:
        early_val = early['attendance'].values[0]
        late_val = late['attendance'].values[0]
        if early_val > 0:
            change_pct = ((late_val - early_val) / early_val) * 100
            insights.append({
                'team': team,
                'change_pct': change_pct,
                'early': early_val,
                'late': late_val
            })

if insights:
    insights_sorted = sorted(insights, key=lambda x: x['change_pct'], reverse=True)
    col_i1, col_i2, col_i3 = st.columns(3)
    with col_i1:
        top = insights_sorted[0]
        st.success(
            f"📈 **Highest Growth**\n\n**{top['team']}**\n\n"
            f"{earliest_year} → {latest_year}\n\n"
            f"{top['early']:,} → {top['late']:,}\n\n"
            f"**{top['change_pct']:+.1f}%**"
        )
    with col_i2:
        bot = insights_sorted[-1]
        st.info(
            f"📉 **Lowest Growth**\n\n**{bot['team']}**\n\n"
            f"{earliest_year} → {latest_year}\n\n"
            f"{bot['early']:,} → {bot['late']:,}\n\n"
            f"**{bot['change_pct']:+.1f}%**"
        )
    with col_i3:
        avg_change = np.mean([x['change_pct'] for x in insights])
        st.warning(
            f"📊 **Selected Teams Avg.**\n\n"
            f"{earliest_year} → {latest_year}\n\n"
            f"Average change\n\n"
            f"**{avg_change:+.1f}%**\n\n"
            f"({len(insights)} teams)"
        )

# ---------- Footer ----------
st.divider()
st.caption(
    "⚾ KBO Attendance Dashboard | Built with Streamlit & scikit-learn | "
    "Data source: KBO Official Records (koreabaseball.com)"
)
