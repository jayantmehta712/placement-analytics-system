from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Annotated

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "placement_data.csv"
MODEL_PATH = ROOT / "models" / "placement_model.joblib"
FRONTEND_PATH = ROOT / "frontend"

FEATURES = [
    "gender",
    "branch",
    "graduation_year",
    "cgpa",
    "tenth_percent",
    "twelfth_percent",
    "internships",
    "projects",
    "certifications",
    "aptitude_score",
    "communication_score",
]

app = FastAPI(
    title="Placement Analytics API",
    description="Backend API for placement analytics, dashboard summaries, and candidate prediction.",
    version="1.0.0",
)


class CandidateProfile(BaseModel):
    gender: str
    branch: str
    graduation_year: int = Field(ge=2021, le=2030)
    cgpa: float = Field(ge=5.0, le=10.0)
    tenth_percent: float = Field(ge=40.0, le=100.0)
    twelfth_percent: float = Field(ge=40.0, le=100.0)
    internships: int = Field(ge=0, le=5)
    projects: int = Field(ge=0, le=8)
    certifications: int = Field(ge=0, le=8)
    aptitude_score: float = Field(ge=0.0, le=100.0)
    communication_score: float = Field(ge=0.0, le=100.0)


@lru_cache(maxsize=1)
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df["placement_date"] = pd.to_datetime(df["placement_date"], errors="coerce")
    df["company"] = df["company"].fillna("")
    df["role"] = df["role"].fillna("")
    return df


@lru_cache(maxsize=1)
def load_model():
    if not MODEL_PATH.exists():
        return None
    return joblib.load(MODEL_PATH)


def clean_records(df: pd.DataFrame) -> list[dict]:
    clean_df = df.copy()
    for column in clean_df.select_dtypes(include=["datetime64[ns]"]).columns:
        clean_df[column] = clean_df[column].dt.strftime("%Y-%m-%d")
    clean_df = clean_df.where(pd.notna(clean_df), None)
    return clean_df.to_dict(orient="records")


def filter_data(
    years: list[int] | None,
    branches: list[str] | None,
    cgpa_min: float | None,
    cgpa_max: float | None,
) -> pd.DataFrame:
    df = load_data()
    filtered = df.copy()

    if years:
        filtered = filtered[filtered["graduation_year"].isin(years)]
    if branches:
        filtered = filtered[filtered["branch"].isin(branches)]
    if cgpa_min is not None:
        filtered = filtered[filtered["cgpa"] >= cgpa_min]
    if cgpa_max is not None:
        filtered = filtered[filtered["cgpa"] <= cgpa_max]

    return filtered


def percentage(value: float) -> float:
    if pd.isna(value):
        return 0.0
    return round(float(value) * 100, 1)


def rounded(value: float, digits: int = 1) -> float:
    if pd.isna(value):
        return 0.0
    return round(float(value), digits)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "rows": len(load_data()), "model_ready": MODEL_PATH.exists()}


@app.get("/api/metadata")
def metadata() -> dict:
    df = load_data()
    return {
        "years": sorted(int(year) for year in df["graduation_year"].unique()),
        "branches": sorted(df["branch"].unique().tolist()),
        "genders": sorted(df["gender"].unique().tolist()),
        "cgpa": {
            "min": rounded(df["cgpa"].min()),
            "max": rounded(df["cgpa"].max()),
        },
    }


@app.get("/api/dashboard")
def dashboard(
    years: Annotated[list[int] | None, Query()] = None,
    branches: Annotated[list[str] | None, Query()] = None,
    cgpa_min: float | None = None,
    cgpa_max: float | None = None,
) -> dict:
    filtered = filter_data(years, branches, cgpa_min, cgpa_max)
    placed = filtered[filtered["placed"] == 1]

    total_students = int(len(filtered))
    placed_students = int(filtered["placed"].sum()) if total_students else 0

    trend = (
        filtered.groupby("graduation_year", as_index=False)
        .agg(total_students=("student_id", "count"), placed_students=("placed", "sum"))
        .assign(
            placement_rate=lambda data: data["placed_students"] / data["total_students"] * 100
        )
        .sort_values("graduation_year")
    )

    branch_summary = (
        filtered.groupby("branch", as_index=False)
        .agg(
            total_students=("student_id", "count"),
            placed_students=("placed", "sum"),
            avg_cgpa=("cgpa", "mean"),
        )
        .assign(
            placement_rate=lambda data: data["placed_students"] / data["total_students"] * 100
        )
        .sort_values("placement_rate", ascending=False)
    )

    company_summary = (
        placed.groupby("company", as_index=False)
        .agg(
            hires=("student_id", "count"),
            avg_package=("package_lpa", "mean"),
            max_package=("package_lpa", "max"),
        )
        .sort_values(["hires", "avg_package"], ascending=False)
        .head(10)
    )

    skill_rows = []
    for _, row in placed.iterrows():
        for skill in str(row["technical_skills"]).split("|"):
            skill_rows.append({"skill": skill.strip(), "package_lpa": row["package_lpa"]})

    skill_summary = pd.DataFrame(skill_rows)
    if not skill_summary.empty:
        skill_summary = (
            skill_summary.groupby("skill", as_index=False)
            .agg(students=("skill", "count"), avg_package=("package_lpa", "mean"))
            .sort_values(["students", "avg_package"], ascending=False)
            .head(10)
        )

    top_offers = placed.sort_values("package_lpa", ascending=False)[
        ["name", "branch", "graduation_year", "company", "role", "package_lpa"]
    ].head(8)

    students = filtered.sort_values(["placed", "package_lpa", "cgpa"], ascending=False)[
        [
            "student_id",
            "name",
            "branch",
            "graduation_year",
            "cgpa",
            "placed",
            "company",
            "role",
            "package_lpa",
            "offer_type",
        ]
    ].head(40)

    return {
        "kpis": {
            "students": total_students,
            "placed": placed_students,
            "placement_rate": percentage(placed_students / total_students) if total_students else 0,
            "avg_package": rounded(placed["package_lpa"].mean()) if not placed.empty else 0,
            "highest_package": rounded(placed["package_lpa"].max()) if not placed.empty else 0,
            "avg_cgpa": rounded(filtered["cgpa"].mean()) if not filtered.empty else 0,
        },
        "trend": clean_records(trend),
        "branch_summary": clean_records(branch_summary),
        "company_summary": clean_records(company_summary),
        "skill_summary": clean_records(skill_summary),
        "salary_distribution": clean_records(placed[["package_lpa", "branch", "company", "name"]]),
        "top_offers": clean_records(top_offers),
        "students": clean_records(students),
    }


@app.post("/api/predict")
def predict(candidate: CandidateProfile) -> dict:
    model = load_model()
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model is not trained yet. Run: python models/train_model.py",
        )

    payload = pd.DataFrame([candidate.model_dump()], columns=FEATURES)
    probability = float(model.predict_proba(payload)[0][1] * 100)
    prediction = int(model.predict(payload)[0])

    return {
        "prediction": prediction,
        "probability": round(probability, 1),
        "message": "Likely to be placed" if prediction else "Placement risk detected",
    }


app.mount("/assets", StaticFiles(directory=FRONTEND_PATH), name="assets")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(FRONTEND_PATH / "index.html")
