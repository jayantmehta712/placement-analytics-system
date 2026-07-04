# Power BI Dashboard Guide

Use `data/placement_data.csv` as the primary source, or connect to `placement_analytics.db` after running `python scripts/create_database.py`.

## Suggested Pages

## 1. Executive Overview

- Cards: Total Students, Placed Students, Placement Rate, Average Package, Highest Package
- Line chart: Placement Rate by Graduation Year
- Bar chart: Branch-wise Placement Rate
- Slicer: Graduation Year, Branch, Gender

## 2. Company Hiring

- Bar chart: Hires by Company
- Matrix: Company, Role, Hires, Average Package, Highest Package
- Treemap: Hiring Share by Company

## 3. Salary Analysis

- Histogram: Package Distribution
- Box plot custom visual: Package by Branch
- Table: Top 10 Offers
- KPI: Highest Package

## 4. Student Readiness

- Scatter chart: CGPA vs Package, colored by Branch
- Bar chart: Placement Rate by CGPA Band
- Column chart: Average Aptitude and Communication Score by Placement Status

## Recommended Measures

```DAX
Total Students = COUNTROWS(placement_data)

Placed Students = CALCULATE(COUNTROWS(placement_data), placement_data[placed] = 1)

Placement Rate = DIVIDE([Placed Students], [Total Students])

Average Package = AVERAGE(placement_data[package_lpa])

Highest Package = MAX(placement_data[package_lpa])
```

For `Average Package`, filter `placed = 1` in the visual so not-placed rows with `0.0` package do not reduce the average.
