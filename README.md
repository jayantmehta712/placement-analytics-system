# Placement Analytics System

A portfolio-ready full-stack analytics project for exploring campus placement outcomes with Python, SQL, FastAPI, machine learning, and a modern browser dashboard.

## Highlights

- Student CGPA and skill analysis
- Placement trends by year, branch, gender, and offer type
- Company-wise hiring and package benchmarking
- Salary distribution and outlier analysis
- Placement prediction using a machine learning model
- SQLite database plus reusable SQL analysis queries
- Power BI-ready CSV exports

## Tech Stack

- Python: data cleaning, analytics, model training
- SQL / SQLite: structured placement database and analysis queries
- FastAPI: backend API for dashboard data and placement prediction
- HTML/CSS/JavaScript: responsive frontend dashboard
- Streamlit: original dashboard kept as an optional legacy app
- Power BI: optional dashboard using exported CSV files
- scikit-learn: placement prediction model

## Project Structure

```text
Placement Analytics System/
  app.py
  backend/
    main.py
  frontend/
    index.html
    styles.css
    app.js
  requirements.txt
  data/
    placement_data.csv
  database/
    schema.sql
    analytics_queries.sql
  models/
    train_model.py
  scripts/
    create_database.py
  reports/
    powerbi_guide.md
```

## Quick Start

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Create the SQLite database:

```bash
python scripts/create_database.py
```

3. Train the prediction model:

```bash
python models/train_model.py
```

4. Run the full-stack app:

```bash
python -m uvicorn backend.main:app --reload
```

5. Open the dashboard:

```text
http://127.0.0.1:8000
```

Optional: run the original Streamlit app:

```bash
streamlit run app.py
```

## Dataset

The included dataset is synthetic but realistic enough for a portfolio demonstration. It includes student academic details, branch, graduation year, internships, projects, skills, placement outcome, company, role, package, and placement date.

## Power BI Usage

Use `data/placement_data.csv` directly in Power BI, or connect Power BI to `placement_analytics.db` after running `scripts/create_database.py`. See `reports/powerbi_guide.md` for suggested dashboard pages and visuals.

## Portfolio Talking Points

- Built an end-to-end analytics workflow from raw student placement data to dashboard insights.
- Used SQL for company-wise hiring, salary benchmarking, placement conversion, and yearly trends.
- Designed a FastAPI backend with reusable JSON endpoints for KPIs, charts, filtered records, and ML scoring.
- Built a responsive frontend dashboard for quick business insights.
- Built a classification model to estimate placement probability from academic and career-readiness indicators.
- Prepared the same data model for Power BI storytelling.
