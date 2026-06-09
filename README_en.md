# ⚾ KBO Attendance Dashboard

An interactive Streamlit dashboard for comparing yearly attendance trends across KBO (Korea Baseball Organization) teams, with future attendance prediction powered by scikit-learn.

## ✨ Features

- 📊 **Yearly attendance comparison** — compare multiple teams on a single line chart
- 🔮 **Future attendance prediction** — linear regression forecasts 1 to 5 years ahead
- 🎚️ **Interactive filters** — freely toggle teams, year range, and prediction options from the sidebar
- 🦠 **COVID year exclusion** — one click removes the 2020-2021 anomaly years from charts, predictions, and insights
- 📈 **Per-year team ranking** — horizontal bar chart for any selected season
- 💡 **Automatic insights** — highest/lowest growth teams and average change rate
- 📋 **Detailed data table** — every figure available in tabular form

## 🚀 How to Run

### Local
```bash
pip install -r requirements.txt
streamlit run app_en.py
```

The app will open automatically at `http://localhost:8501`.

### Streamlit Cloud
1. Push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository and set `app_en.py` as the main file
4. Click **Deploy**

## 📂 Project Structure

```
kbo-attendance-dashboard/
├── app_en.py              # Main Streamlit application (English)
├── kbo_attendance.csv     # Yearly attendance data per team
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## 🔮 Prediction Model

The forecast uses **Linear Regression** from scikit-learn.

- A separate model is fit for each team
- Training data: the actual attendance figures within the selected year range
- The **"Exclude COVID years (2020-2021)"** checkbox is recommended for cleaner predictions, since those years were heavily distorted by the pandemic
- Predicted years are shown as dashed lines, and the confidence (R²) is reported in the prediction summary table

### Why Linear Regression?
- With only ~10-12 data points per team, a simple model is more reliable than a complex one
- The main goal is trend identification, so sophisticated time-series models would risk overfitting
- Results are easy to interpret

## 📊 Data Source

Data is based on **KBO Official Records** ([koreabaseball.com](https://www.koreabaseball.com/Record/Crowd/GraphYear.aspx)).

### Data Schema (`kbo_attendance.csv`)
| Column | Description |
|--------|-------------|
| `year` | Season year |
| `team` | Team name (English short) |
| `team_kr` | Team name (Korean) |
| `stadium` | Home stadium (English) |
| `stadium_kr` | Home stadium (Korean) |
| `attendance` | Total season attendance |
| `games` | Number of home games |

### Note on Team History
Two franchises have changed sponsor names over the years. The dashboard unifies them under their current names:
- **Nexen Heroes** (through 2018) → **Kiwoom Heroes** (2019-present)
- **SK Wyverns** (through 2020) → **SSG Landers** (2021-present)

The player rosters and franchises are continuous; only the sponsor names changed.

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
