# ⚾ KBO Attendance Dashboard

A Streamlit web dashboard for comparing yearly attendance trends across KBO (Korea Baseball Organization) teams, with future attendance prediction powered by scikit-learn.

KBO 구단별 연도별 관중 수 추이를 비교하고 미래 관중 수를 예측하는 인터랙티브 웹 대시보드입니다.

## ✨ Features

- 📊 **연도별 관중 추이 비교** — 여러 구단의 관중 변화를 라인 차트로 비교
- 🔮 **미래 관중 예측** — Linear Regression 기반으로 향후 1~5년 예측
- 🎚️ **인터랙티브 필터** — 구단, 연도 범위, 예측 옵션을 사이드바에서 자유롭게 조절
- 📈 **연도별 비교 막대그래프** — 특정 연도의 구단 순위 시각화
- 💡 **자동 인사이트** — 최대/최소 성장 구단 및 평균 변동률 자동 계산
- 📋 **상세 데이터 테이블** — 모든 수치를 표 형태로 확인 가능

## 🚀 How to Run

### Local
```bash
pip install -r requirements.txt
streamlit run app.py
```

브라우저가 자동으로 열리며 `http://localhost:8501` 에서 앱이 실행됩니다.

### Streamlit Cloud
1. 이 저장소를 GitHub에 푸시
2. [share.streamlit.io](https://share.streamlit.io) 접속
3. GitHub 저장소 연결 후 `app.py` 지정 → Deploy

## 📂 Project Structure

```
kbo-attendance-dashboard/
├── app.py                  # Main Streamlit application
├── kbo_attendance.csv      # Yearly attendance data per team
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## 🔮 Prediction Model

미래 관중 수 예측은 **Linear Regression (선형 회귀)** 을 사용합니다.

- 각 구단별로 독립적인 모델을 학습
- 학습 데이터: 선택한 연도 범위의 실제 관중 수
- **COVID 영향 연도(2020-2021) 제외 옵션** 권장 (코로나19로 인한 비정상 수치)
- 예측 결과는 점선으로 표시되며, 신뢰도(R²)는 예측 요약 표에서 확인 가능

### 왜 Linear Regression?
- 연도별 데이터 포인트가 적기 때문(10~12개) 단순 모델이 더 신뢰성 있음
- 트렌드 파악이 주 목적이므로 복잡한 시계열 모델은 과적합 위험
- 결과 해석이 직관적

## 📊 Data Source

데이터는 **KBO 공식 기록** ([koreabaseball.com](https://www.koreabaseball.com/Record/Crowd/GraphYear.aspx)) 을 기반으로 작성되었습니다.

> ⚠️ **Note**: 일부 수치는 추정치이거나 보도 자료 기반입니다. 정확한 수치는 KBO 공식 자료에서 확인 후 `kbo_attendance.csv`를 직접 업데이트하시기 바랍니다.

### Data Schema (`kbo_attendance.csv`)
| Column | Description |
|--------|-------------|
| `year` | 시즌 연도 |
| `team` | 구단명 (영문) |
| `team_kr` | 구단명 (한글) |
| `stadium` | 홈구장 (영문) |
| `stadium_kr` | 홈구장 (한글) |
| `attendance` | 시즌 총 관중 수 |
| `games` | 홈경기 수 |

## 🛠️ Tech Stack

- **Streamlit** — Web framework
- **Pandas** — Data manipulation
- **Plotly** — Interactive charts
- **scikit-learn** — Linear regression for prediction
- **NumPy** — Numerical computing

## 👤 Author

**[Your Name]**
Student ID: [Your Student ID]
Course: Arts and Big Data — Sungkyunkwan University
Instructor: Prof. Jahwan Koo

## 📜 License

This project is for educational purposes. Data ownership belongs to KBO.
