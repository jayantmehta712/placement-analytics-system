from pathlib import Path

import joblib
import pandas as pd
import plotly.express as px
import streamlit as st


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "placement_data.csv"
MODEL_PATH = ROOT / "models" / "placement_model.joblib"


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df["placement_date"] = pd.to_datetime(df["placement_date"], errors="coerce")
    return df


def placement_rate(series: pd.Series) -> float:
    return round(series.mean() * 100, 1)


def format_lpa(value: float) -> str:
    if pd.isna(value):
        return "0.0 LPA"
    return f"{value:.1f} LPA"


def main() -> None:
    st.set_page_config(
        page_title="Placement Analytics System",
        page_icon="PAS",
        layout="wide",
    )

    df = load_data()
    placed_df = df[df["placed"] == 1]

    st.title("Placement Analytics System")
    st.caption("Python + SQL + Streamlit dashboard for campus placement insights")

    with st.sidebar:
        st.header("Filters")
        years = sorted(df["graduation_year"].unique())
        branches = sorted(df["branch"].unique())
        selected_years = st.multiselect("Graduation year", years, default=years)
        selected_branches = st.multiselect("Branch", branches, default=branches)
        cgpa_range = st.slider(
            "CGPA range",
            min_value=float(df["cgpa"].min()),
            max_value=float(df["cgpa"].max()),
            value=(float(df["cgpa"].min()), float(df["cgpa"].max())),
            step=0.1,
        )

    filtered = df[
        df["graduation_year"].isin(selected_years)
        & df["branch"].isin(selected_branches)
        & df["cgpa"].between(cgpa_range[0], cgpa_range[1])
    ]
    filtered_placed = filtered[filtered["placed"] == 1]

    total_students = len(filtered)
    placed_students = int(filtered["placed"].sum()) if total_students else 0
    rate = placement_rate(filtered["placed"]) if total_students else 0
    avg_package = filtered_placed["package_lpa"].mean() if not filtered_placed.empty else 0
    highest_package = filtered_placed["package_lpa"].max() if not filtered_placed.empty else 0

    kpi_1, kpi_2, kpi_3, kpi_4 = st.columns(4)
    kpi_1.metric("Students", f"{total_students}")
    kpi_2.metric("Placed", f"{placed_students}", f"{rate}%")
    kpi_3.metric("Average Package", format_lpa(avg_package))
    kpi_4.metric("Highest Package", format_lpa(highest_package))

    tab_overview, tab_companies, tab_salary, tab_predict = st.tabs(
        ["Overview", "Company Hiring", "Salary Analysis", "Prediction"]
    )

    with tab_overview:
        col_1, col_2 = st.columns(2)
        trend = (
            filtered.groupby("graduation_year", as_index=False)
            .agg(total_students=("student_id", "count"), placed_students=("placed", "sum"))
            .assign(placement_rate=lambda data: data["placed_students"] / data["total_students"] * 100)
        )
        branch = (
            filtered.groupby("branch", as_index=False)
            .agg(total_students=("student_id", "count"), placed_students=("placed", "sum"), avg_cgpa=("cgpa", "mean"))
            .assign(placement_rate=lambda data: data["placed_students"] / data["total_students"] * 100)
        )

        with col_1:
            st.subheader("Placement Trend")
            st.plotly_chart(
                px.line(
                    trend,
                    x="graduation_year",
                    y="placement_rate",
                    markers=True,
                    labels={"graduation_year": "Year", "placement_rate": "Placement Rate (%)"},
                ),
                use_container_width=True,
            )

        with col_2:
            st.subheader("Branch-wise Placement")
            st.plotly_chart(
                px.bar(
                    branch,
                    x="branch",
                    y="placement_rate",
                    color="avg_cgpa",
                    labels={"branch": "Branch", "placement_rate": "Placement Rate (%)", "avg_cgpa": "Avg CGPA"},
                ),
                use_container_width=True,
            )

        st.subheader("CGPA vs Package")
        st.plotly_chart(
            px.scatter(
                filtered,
                x="cgpa",
                y="package_lpa",
                color="branch",
                size="aptitude_score",
                hover_data=["name", "company", "role"],
                labels={"cgpa": "CGPA", "package_lpa": "Package (LPA)"},
            ),
            use_container_width=True,
        )

    with tab_companies:
        company_summary = (
            filtered_placed.groupby("company", as_index=False)
            .agg(hires=("student_id", "count"), avg_package=("package_lpa", "mean"), max_package=("package_lpa", "max"))
            .sort_values(["hires", "avg_package"], ascending=False)
        )

        col_1, col_2 = st.columns(2)
        with col_1:
            st.subheader("Company-wise Hiring")
            st.plotly_chart(
                px.bar(company_summary, x="company", y="hires", labels={"company": "Company", "hires": "Hires"}),
                use_container_width=True,
            )
        with col_2:
            st.subheader("Average Package by Company")
            st.plotly_chart(
                px.bar(
                    company_summary,
                    x="company",
                    y="avg_package",
                    color="avg_package",
                    labels={"company": "Company", "avg_package": "Average Package (LPA)"},
                ),
                use_container_width=True,
            )

        st.dataframe(company_summary, use_container_width=True, hide_index=True)

    with tab_salary:
        col_1, col_2 = st.columns(2)
        with col_1:
            st.subheader("Salary Distribution")
            st.plotly_chart(
                px.histogram(filtered_placed, x="package_lpa", nbins=10, labels={"package_lpa": "Package (LPA)"}),
                use_container_width=True,
            )
        with col_2:
            st.subheader("Package by Branch")
            st.plotly_chart(
                px.box(filtered_placed, x="branch", y="package_lpa", labels={"branch": "Branch", "package_lpa": "Package (LPA)"}),
                use_container_width=True,
            )

        st.subheader("Top Offers")
        top_offers = filtered_placed.sort_values("package_lpa", ascending=False)[
            ["name", "branch", "graduation_year", "company", "role", "package_lpa"]
        ].head(10)
        st.dataframe(top_offers, use_container_width=True, hide_index=True)

    with tab_predict:
        st.subheader("Placement Prediction")

        if not MODEL_PATH.exists():
            st.warning("Train the model first with: python models/train_model.py")
        else:
            model = joblib.load(MODEL_PATH)
            col_1, col_2, col_3 = st.columns(3)
            with col_1:
                gender = st.selectbox("Gender", sorted(df["gender"].unique()))
                branch_value = st.selectbox("Branch", sorted(df["branch"].unique()))
                graduation_year = st.number_input("Graduation Year", min_value=2021, max_value=2030, value=2026)
            with col_2:
                cgpa = st.slider("CGPA", 5.0, 10.0, 8.0, 0.1)
                tenth = st.slider("10th Percentage", 40, 100, 85)
                twelfth = st.slider("12th Percentage", 40, 100, 82)
            with col_3:
                internships = st.number_input("Internships", min_value=0, max_value=5, value=1)
                projects = st.number_input("Projects", min_value=0, max_value=8, value=3)
                certifications = st.number_input("Certifications", min_value=0, max_value=8, value=2)

            aptitude = st.slider("Aptitude Score", 0, 100, 75)
            communication = st.slider("Communication Score", 0, 100, 78)

            candidate = pd.DataFrame(
                [
                    {
                        "gender": gender,
                        "branch": branch_value,
                        "graduation_year": graduation_year,
                        "cgpa": cgpa,
                        "tenth_percent": tenth,
                        "twelfth_percent": twelfth,
                        "internships": internships,
                        "projects": projects,
                        "certifications": certifications,
                        "aptitude_score": aptitude,
                        "communication_score": communication,
                    }
                ]
            )

            probability = model.predict_proba(candidate)[0][1] * 100
            prediction = model.predict(candidate)[0]

            st.metric("Placement Probability", f"{probability:.1f}%")
            if prediction == 1:
                st.success("Likely to be placed based on the current profile.")
            else:
                st.error("Placement risk detected. Improve projects, internships, aptitude, and communication score.")

    with st.expander("View Filtered Dataset"):
        st.dataframe(filtered, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
