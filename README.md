# Placement Analytics System

A full-stack campus placement analytics platform for exploring student outcomes, recruiter trends, salary benchmarks, and placement probability.

The project combines a FastAPI backend, a responsive browser dashboard, SQLite-backed data, reusable SQL analysis queries, and a scikit-learn prediction model. It is designed as a portfolio-ready analytics project for interviews and demonstrations.

## Key Features

- Interactive dashboard for placement KPIs, branch performance, salary spread, and recruiter hiring.
- Filter analytics by graduation year, branch, and CGPA range.
- Candidate placement scorer powered by a trained machine learning pipeline.
- REST API endpoints for metadata, dashboard summaries, health checks, and predictions.
- SQLite database schema plus reusable analytics SQL queries.
- Original Streamlit dashboard retained as an optional legacy interface.
- Power BI guide for turning the same dataset into BI reports.

## Tech Stack

| Layer | Tools |
| --- | --- |
| Frontend | HTML, CSS, JavaScript, Chart.js, Lucide Icons |
| Backend | Python, FastAPI, Pydantic |
| Data | Pandas, SQLite, SQL |
| Machine Learning | scikit-learn, joblib |
| Optional Dashboard | Streamlit, Plotly |

## Project Structure

```text
Placement Analytics System/
  backend/
    main.py                  # FastAPI backend and API routes
  frontend/
    index.html               # Dashboard UI
    styles.css               # Responsive styling
    app.js                   # API calls, charts, filters, prediction form
  data/
    placement_data.csv       # Synthetic placement dataset
  database/
    schema.sql               # SQLite schema
    analytics_queries.sql    # SQL analysis queries
  models/
    train_model.py           # Model training pipeline
    placement_model.joblib   # Trained placement prediction model
    model_metrics.txt        # Model evaluation output
  reports/
    powerbi_guide.md         # Power BI dashboard guidance
  scripts/
    create_database.py       # CSV-to-SQLite loader
  app.py                     # Optional Streamlit dashboard
  placement_analytics.db     # SQLite database
  requirements.txt
```

## Quick Start

1. Install dependencies.

```bash
pip install -r requirements.txt
```

2. Recreate the SQLite database.

```bash
python scripts/create_database.py
```

3. Train or refresh the prediction model.

```bash
python models/train_model.py
```

4. Run the full-stack app.

```bash
python -m uvicorn backend.main:app --reload
```

5. Open the dashboard.

```text
http://127.0.0.1:8000
```

## API Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/health` | Check API status, dataset row count, and model availability |
| GET | `/api/metadata` | Get branches, years, genders, and CGPA range for filters |
| GET | `/api/dashboard` | Get KPIs, chart data, top offers, skills, and student records |
| POST | `/api/predict` | Predict placement probability for a candidate profile |

Example prediction request:

```json
{
  "gender": "Female",
  "branch": "CSE",
  "graduation_year": 2026,
  "cgpa": 8.7,
  "tenth_percent": 91,
  "twelfth_percent": 88,
  "internships": 2,
  "projects": 4,
  "certifications": 3,
  "aptitude_score": 84,
  "communication_score": 86
}
```

## Dataset

The included dataset is synthetic but realistic enough for a portfolio demonstration. It contains student academics, branch, graduation year, internships, projects, certifications, technical skills, placement status, company, role, package, offer type, and placement date.

## Machine Learning

The prediction model uses a scikit-learn pipeline with:

- Standard scaling for numeric features.
- One-hot encoding for categorical features.
- Random Forest classification for placement prediction.
- Evaluation output saved in `models/model_metrics.txt`.

Model features include CGPA, 10th and 12th percentages, internships, projects, certifications, aptitude score, communication score, gender, branch, and graduation year.

## Optional Streamlit App

The original Streamlit dashboard can still be run with:

```bash
streamlit run app.py
```

## Power BI Usage

Use `data/placement_data.csv` directly in Power BI, or connect Power BI to `placement_analytics.db` after running `scripts/create_database.py`. See `reports/powerbi_guide.md` for suggested report pages and visuals.

## Interview Talking Points

- Built an end-to-end analytics workflow from raw placement data to dashboard insights.
- Designed a FastAPI backend with reusable JSON endpoints for analytics and prediction.
- Created a responsive frontend dashboard with filters, charts, KPI cards, top offers, and candidate scoring.
- Used SQL for placement conversion, recruiter analysis, salary benchmarking, and trend analysis.
- Trained and served a machine learning model for placement probability estimation.
- Prepared the same data model for dashboarding in both a custom web app and Power BI.

## Future Improvements

- Add authentication for placement officers and department users.
- Add CSV upload so colleges can analyze their own placement data.
- Store prediction history and candidate profiles in the database.
- Add automated tests for API endpoints and model input validation.
