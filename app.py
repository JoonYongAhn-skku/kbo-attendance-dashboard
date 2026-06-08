"""
KBO Attendance Dashboard
구단별 연도별 관중 수 추이 비교 및 예측 대시보드

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
    .metric-card {
        background: linear-gradient(135deg, #1F3864 0%, #2E75B6 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        color: white;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.6rem;
    }
</style>
""", unsafe_allow_html=True)

# ---------- Team Colors (official-ish team colors) ----------
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

# ---------- Data Loading ----------
@st.cache_data
def load_data():
    """Load KBO attendance data from CSV."""
    csv_path = Path(__file__).parent / "kbo_attendance.csv"
    df = pd.read_csv(csv_path)
    # Add per-game average
    df['avg_per_game'] = (df['attendance'] / df['games']).round(0).astype(int)
    return df

df = load_data()

# ---------- Header ----------
st.markdown('<p class="main-title">⚾ KBO Attendance Dashboard</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">한국프로야구 구단별 연도별 관중 수 추이 비교 및 미래 예측</p>',
    unsafe_allow_html=True
)

# ---------- Sidebar ----------
st.sidebar.header("⚙️ 필터 설정")

# Team selection
all_teams = sorted(df['team'].unique().tolist())
team_kr_map = dict(zip(df['team'], df['team_kr']))

st.sidebar.subheader("구단 선택")
select_all = st.sidebar.checkbox("전체 구단 선택", value=False)

if select_all:
    selected_teams = all_teams
else:
    selected_teams = st.sidebar.multiselect(
        "비교할 구단을 선택하세요",
        options=all_teams,
        default=['LG', 'Doosan', 'KIA', 'Lotte'],
        format_func=lambda x: f"{x} ({team_kr_map.get(x, x)})"
    )

# Year range
st.sidebar.subheader("연도 범위")
min_year, max_year = int(df['year'].min()), int(df['year'].max())
year_range = st.sidebar.slider(
    "분석할 연도 구간",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
    step=1
)

# COVID exclusion (applies to chart, prediction, and insights)
exclude_covid = st.sidebar.checkbox(
    "🦠 코로나 연도(2020-2021) 제외",
    value=False,
    help="2020-2021년은 코로나19로 인해 비정상적으로 낮은 관중 수치를 보였습니다. "
         "체크하면 차트, 예측, 인사이트 모두에서 해당 연도가 제외됩니다."
)

# Prediction settings
st.sidebar.divider()
st.sidebar.subheader("🔮 미래 관중 예측")
enable_prediction = st.sidebar.toggle("예측 기능 활성화", value=False)

prediction_years = 3
if enable_prediction:
    prediction_years = st.sidebar.slider(
        "예측 연수",
        min_value=1, max_value=5, value=3,
        help="몇 년 뒤까지 예측할지 선택하세요."
    )

# Info box
st.sidebar.divider()
st.sidebar.caption(
    "📊 **데이터 출처**\n\n"
    "KBO 공식 기록 (koreabaseball.com)"
)

# ---------- Stop if no team selected ----------
if not selected_teams:
    st.warning("⚠️ 사이드바에서 비교할 구단을 하나 이상 선택해주세요.")
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
    st.metric("총 관중 수", f"{total_attendance:,}명")
with col2:
    avg_per_game = int(filtered['avg_per_game'].mean())
    st.metric("평균 경기당 관중", f"{avg_per_game:,}명")
with col3:
    st.metric("선택 구단 수", f"{len(selected_teams)}개")
with col4:
    span = year_range[1] - year_range[0] + 1
    st.metric("분석 연도 수", f"{span}년")

st.divider()

# ---------- Main Chart: Line Chart with Predictions ----------
st.subheader("📈 연도별 관중 수 추이")

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
        hovertemplate=f"<b>{team}</b><br>%{{x}}년: %{{y:,}}명<extra></extra>"
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
                name=f'{team} (예측)',
                line=dict(color=color, width=2, dash='dash'),
                marker=dict(size=8, symbol='diamond-open'),
                hovertemplate=f"<b>{team} 예측</b><br>%{{x}}년: %{{y:,.0f}}명<extra></extra>"
            ))

            # Record for summary
            growth_rate = (model.coef_[0] / model.intercept_) * 100 if model.intercept_ != 0 else 0
            prediction_summary.append({
                '구단': team,
                f'{last_year}년 (실제)': f"{last_value:,}명",
                f'{future_years_arr[-1]}년 (예측)': f"{int(predictions[-1]):,}명",
                '연평균 증감': f"{int(model.coef_[0]):+,}명/년",
                'R²': f"{model.score(X, y):.3f}"
            })

fig.update_layout(
    xaxis_title="연도",
    yaxis_title="관중 수 (명)",
    hovermode='x unified',
    template='plotly_white',
    height=520,
    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
)
fig.update_yaxes(tickformat=',')

st.plotly_chart(fig, use_container_width=True)

# ---------- Prediction Summary Table ----------
if enable_prediction and prediction_summary:
    st.subheader("🔮 예측 요약")
    pred_df = pd.DataFrame(prediction_summary)
    st.dataframe(pred_df, use_container_width=True, hide_index=True)
    st.caption(
        "💡 **R² 값 해석**: 1에 가까울수록 선형 모델이 데이터를 잘 설명함. "
        "0.7 이상이면 예측이 어느 정도 신뢰할 만한 수준입니다."
    )

st.divider()

# ---------- Side-by-side: Bar Chart + Table ----------
col_left, col_right = st.columns([1.3, 1])

with col_left:
    st.subheader("📊 연도별 구단 비교 (막대그래프)")
    bar_year = st.selectbox(
        "비교할 연도 선택",
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
        hovertemplate="<b>%{y}</b><br>%{x:,}명<extra></extra>"
    ))
    fig_bar.update_layout(
        xaxis_title=f"{bar_year}년 관중 수",
        yaxis_title="",
        template='plotly_white',
        height=420,
        showlegend=False,
        margin=dict(l=0, r=80, t=20, b=0)
    )
    fig_bar.update_xaxes(tickformat=',')
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.subheader("📋 상세 데이터")
    display_df = filtered[['year', 'team', 'team_kr', 'stadium_kr', 'attendance', 'avg_per_game']].copy()
    display_df.columns = ['연도', '구단', '구단(한글)', '구장', '총 관중', '경기당 평균']
    display_df['총 관중'] = display_df['총 관중'].apply(lambda x: f"{x:,}")
    display_df['경기당 평균'] = display_df['경기당 평균'].apply(lambda x: f"{x:,}")
    st.dataframe(
        display_df.sort_values(['연도', '구단'], ascending=[False, True]),
        use_container_width=True,
        hide_index=True,
        height=420
    )

# ---------- Insights ----------
st.divider()
st.subheader("💡 주요 인사이트")

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
            f"📈 **최대 성장 구단**\n\n**{top['team']}**\n\n"
            f"{earliest_year}년 → {latest_year}년\n\n"
            f"{top['early']:,} → {top['late']:,}명\n\n"
            f"**{top['change_pct']:+.1f}%**"
        )
    with col_i2:
        bot = insights_sorted[-1]
        st.info(
            f"📉 **최소 성장 구단**\n\n**{bot['team']}**\n\n"
            f"{earliest_year}년 → {latest_year}년\n\n"
            f"{bot['early']:,} → {bot['late']:,}명\n\n"
            f"**{bot['change_pct']:+.1f}%**"
        )
    with col_i3:
        avg_change = np.mean([x['change_pct'] for x in insights])
        st.warning(
            f"📊 **선택 구단 평균**\n\n"
            f"{earliest_year}년 → {latest_year}년\n\n"
            f"평균 변동률\n\n"
            f"**{avg_change:+.1f}%**\n\n"
            f"({len(insights)}개 구단 기준)"
        )

# ---------- Footer ----------
st.divider()
st.caption(
    "⚾ KBO Attendance Dashboard | Built with Streamlit & scikit-learn | "
    "Data source: KBO Official Records (koreabaseball.com)"
)
