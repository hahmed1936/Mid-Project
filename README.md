# ✈️ Airline Passenger Satisfaction — Mid Project

An end-to-end data analysis project: **data assessment → cleaning → exploratory analysis → interactive dashboard → presentation**.
Built as the Mid Project of the **Epsilon AI** Data Science program.

> 🔗 **Epsilon AI main repo:** _add the link to the main Epsilon AI repository here_

## 🔗 Links
| Deliverable | Link |
|---|---|
| Jupyter notebook | [`Mid-Project-Script.ipynb`](Mid-Project-Script.ipynb) |
| Streamlit dashboard (public) | _add your Streamlit Community Cloud link here_ |
| Presentation | [`Airline_Satisfaction_Presentation.pptx`](Airline_Satisfaction_Presentation.pptx) |
| Video walkthrough | _add your video link here_ |

## 📂 Repository structure
| File | Description |
|---|---|
| `Data.csv` | Raw dataset (25,976 passengers × 25 columns) |
| `Data_Cleaned.csv` | Cleaned dataset produced by the notebook (used by the dashboard) |
| `Mid-Project-Script.ipynb` | Full analysis: assessment, cleaning, univariate, bivariate & multivariate analysis, conclusions |
| `app.py` | Interactive Streamlit dashboard (7 tabs, 30+ charts: satisfaction bars, gauges, passenger-profile ranking, radar, animated bars, heatmaps) |
| `.streamlit/config.toml` | Dashboard theme |
| `requirements.txt` | Packages needed to run the dashboard |
| `Airline_Satisfaction_Presentation.pptx` | Discussion presentation (English) |

## ❓ Research questions
1. What share of passengers are satisfied?
2. How does satisfaction differ across passenger segments (gender, loyalty, travel type, class, age)?
3. Which services have the strongest relationship with satisfaction?
4. Do departure / arrival delays reduce satisfaction?
5. Does flight distance affect satisfaction, and does the effect depend on class?
6. Which combination of travel type and class gives the happiest / unhappiest passengers?

## 🧹 Data problems found and fixed
| Problem | Fix |
|---|---|
| 83 missing `Arrival Delay in Minutes` | Filled with the passenger's departure delay (r = 0.96) |
| Arrival delay stored as float | Converted to int |
| Ratings of `0` = "Not Applicable" (4,000+ values) | Replaced with NaN so they don't distort averages |
| Inconsistent labels (`disloyal Customer`, `Business travel`, `Eco`) | Standardised |
| Useless `Unnamed: 0` index column | Dropped |
| Column names with spaces and slashes | Converted to snake_case |
| Extreme delay / distance outliers | Verified as genuine, kept and binned |
| Text columns | Converted to ordered categories |

## 💡 Key insights
- Only **43.9 %** of passengers are satisfied.
- **Business class: 69.5 %** satisfied vs **Economy: 19.4 %**.
- **Personal travellers are satisfied in only ~10 %** of cases — in every class.
- **Online boarding**, **inflight entertainment**, **wifi** and **seat comfort** separate satisfied from dissatisfied passengers the most; **wifi is the lowest-rated service**.
- Delays reduce satisfaction from **47.9 %** (on time) to **35.2 %** (> 1 hour late) — a real but weak effect.
- Long-haul passengers look happier, but mostly because they fly **Business class**.
- **Gender has no effect** on satisfaction.

## ▶️ How to run
```bash
pip install -r requirements.txt seaborn scipy jupyter
jupyter notebook Mid-Project-Script.ipynb   # the analysis
streamlit run app.py                        # the dashboard
```

## 🛠️ Tools
Python · Pandas · NumPy · Matplotlib · Seaborn · SciPy · Plotly · Streamlit

## 📊 Dataset
Airline Passenger Satisfaction survey (publicly available on Kaggle).
