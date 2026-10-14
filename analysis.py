"""
CPS School Climate & Attendance Analysis
----------------------------------------
Question: How are chronic truancy, school climate (5Essentials survey), and
other school conditions related across Chicago Public Schools?

Data: "Chicago Public Schools - School Progress Reports" (Chicago Data Portal,
dataset id 2dn2-x66j). Public data, no student-level information.

Usage:
    python analysis.py                 # downloads the CSV directly
    python analysis.py my_file.csv     # or use a CSV you downloaded yourself

Outputs are written to ./outputs
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

URL = "https://data.cityofchicago.org/api/views/2dn2-x66j/rows.csv?accessType=DOWNLOAD"
OUT = Path("outputs")
OUT.mkdir(exist_ok=True)

# Survey ratings are text; convert to ordered scores so they can be analyzed.
# "NOT ENOUGH DATA" is deliberately left unmapped -> missing, not zero.
CLIMATE_MAP = {"NOT YET ORGANIZED": 1, "PARTIALLY ORGANIZED": 2,
               "MODERATELY ORGANIZED": 3, "ORGANIZED": 4, "WELL ORGANIZED": 5}
LIKERT_MAP = {"VERY WEAK": 1, "WEAK": 2, "NEUTRAL": 3, "STRONG": 4, "VERY STRONG": 5}

NUMERIC_COLS = [
    "chronic_truancy_pct", "student_attendance_year_2_pct",
    "teacher_attendance_year_2_pct", "mobility_rate_pct",
    "suspensions_per_100_students_year_2_pct",
    "graduation_4_year_school_pct_year_2",
    "freshmen_on_track_school_pct_year_2", "sat_grade_11_score_school_avg",
]


def load(path=None):
    df = pd.read_csv(path or URL)
    # Standardize headers so small naming differences don't break the script.
    df.columns = df.columns.str.strip().str.lower().str.replace(r"\W+", "_", regex=True)
    return df


def clean(df):
    """Clean the data and return (clean_df, data_quality_log)."""
    log = [f"Rows loaded: {len(df)}"]
    df = df.copy()

    for c in NUMERIC_COLS:
        df[c] = pd.to_numeric(df[c], errors="coerce")  # text -> number, bad -> NaN

    # SAT average of 0 means "no score reported", not a real score of zero.
    zeros = (df["sat_grade_11_score_school_avg"] == 0).sum()
    df.loc[df["sat_grade_11_score_school_avg"] == 0, "sat_grade_11_score_school_avg"] = np.nan
    log.append(f"SAT averages equal to 0 recoded as missing: {zeros}")

    # Schools with too little data to publish a progress report.
    if "empty_progress_report_message" in df.columns:
        n_empty = df["empty_progress_report_message"].notna().sum()
        df = df[df["empty_progress_report_message"].isna()]
        log.append(f"Schools with no progress report removed: {n_empty}")

    df["climate_score"] = df["culture_climate_rating"].str.upper().map(CLIMATE_MAP)
    df["safety_score"] = df["school_survey_safety"].str.upper().map(LIKERT_MAP)

    dupes = df["school_id"].duplicated().sum()
    log.append(f"Duplicate school IDs: {dupes}")
    df = df.drop_duplicates("school_id")
    log.append(f"Rows after cleaning: {len(df)}")
    return df, log


def missingness(df):
    cols = NUMERIC_COLS + ["climate_score", "safety_score"]
    m = (df[cols].isna().mean() * 100).round(1).rename("pct_missing")
    return m.sort_values(ascending=False)


def describe_by_group(df, group):
    g = df.groupby(group).agg(
        schools=("school_id", "count"),
        median_truancy=("chronic_truancy_pct", "median"),
        mean_attendance=("student_attendance_year_2_pct", "mean"),
    ).round(1)
    return g[g["schools"] >= 5].sort_values("median_truancy", ascending=False)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else None
    df, log = clean(load(path))
    (OUT / "data_quality_log.txt").write_text("\n".join(log))
    missingness(df).to_csv(OUT / "missingness.csv")
    df.to_csv(OUT / "cleaned_schools.csv", index=False)

    lines = ["CPS SCHOOL CLIMATE & ATTENDANCE - KEY RESULTS", "=" * 50, ""]
    lines += log + [""]

    # 1. Descriptives
    lines.append("Median chronic truancy by school level:")
    lines.append(describe_by_group(df, "primary_category").to_string())
    lines.append("")
    by_type = describe_by_group(df, "school_type")
    lines.append("Median chronic truancy by school type (types with 5+ schools):")
    lines.append(by_type.to_string())
    lines.append("")

    # 2. Rank (Spearman) correlations - robust to skew and ordinal survey scores
    corr_cols = ["chronic_truancy_pct", "student_attendance_year_2_pct",
                 "teacher_attendance_year_2_pct", "mobility_rate_pct",
                 "suspensions_per_100_students_year_2_pct",
                 "climate_score", "safety_score"]
    corr = df[corr_cols].corr(method="spearman").round(2)
    corr.to_csv(OUT / "spearman_correlations.csv")
    lines.append("Spearman correlations:")
    lines.append(corr.to_string())
    lines.append("")

    # 3. Regression: what is associated with chronic truancy?
    model_df = df.dropna(subset=["chronic_truancy_pct", "safety_score",
                                 "climate_score", "mobility_rate_pct"])
    model = smf.ols(
        "chronic_truancy_pct ~ safety_score + climate_score + mobility_rate_pct"
        " + C(primary_category)", data=model_df
    ).fit(cov_type="HC3")  # robust standard errors
    (OUT / "regression_summary.txt").write_text(str(model.summary()))
    lines.append(f"OLS regression (n={int(model.nobs)}): R-squared = {model.rsquared:.2f}")
    lines.append(model.params.round(2).to_string())
    lines.append("")

    # 4. High schools: freshmen on-track vs 4-year graduation
    hs = df[df["primary_category"] == "HS"].dropna(
        subset=["freshmen_on_track_school_pct_year_2", "graduation_4_year_school_pct_year_2"])
    if len(hs) > 10:
        r, p = stats.pearsonr(hs["freshmen_on_track_school_pct_year_2"],
                              hs["graduation_4_year_school_pct_year_2"])
        lines.append(f"High schools (n={len(hs)}): freshmen on-track vs 4-yr graduation "
                     f"r = {r:.2f}, p = {p:.3g}")

    (OUT / "summary.txt").write_text("\n".join(lines))
    print("\n".join(lines))

    # ---- Charts ----
    plot_df = df[df["school_type"].isin(by_type.index)].dropna(subset=["chronic_truancy_pct"])
    order = by_type.index.tolist()
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.boxplot([plot_df.loc[plot_df["school_type"] == t, "chronic_truancy_pct"] for t in order])
    ax.set_xticks(range(1, len(order) + 1))
    ax.set_xticklabels(order)
    ax.set_ylabel("Chronic truancy (%)")
    ax.set_title("Chronic truancy by school type")
    plt.setp(ax.get_xticklabels(), rotation=35, ha="right")
    fig.tight_layout()
    fig.savefig(OUT / "truancy_by_school_type.png", dpi=150)
    plt.close(fig)

    s = df.dropna(subset=["chronic_truancy_pct", "safety_score"])
    fig, ax = plt.subplots(figsize=(7, 5))
    jitter = np.random.default_rng(1).uniform(-0.15, 0.15, len(s))
    ax.scatter(s["safety_score"] + jitter, s["chronic_truancy_pct"], alpha=0.5)
    ax.set_xlabel("Student-reported safety (1 = very weak, 5 = very strong)")
    ax.set_ylabel("Chronic truancy (%)")
    ax.set_title("Safety rating vs chronic truancy")
    fig.tight_layout()
    fig.savefig(OUT / "safety_vs_truancy.png", dpi=150)
    plt.close(fig)

    if len(hs) > 10:
        fig, ax = plt.subplots(figsize=(7, 5))
        x, y = hs["freshmen_on_track_school_pct_year_2"], hs["graduation_4_year_school_pct_year_2"]
        ax.scatter(x, y, alpha=0.6)
        slope, intercept = np.polyfit(x, y, 1)
        xs = np.linspace(x.min(), x.max(), 50)
        ax.plot(xs, slope * xs + intercept, color="black")
        ax.set_xlabel("Freshmen on track (%)")
        ax.set_ylabel("4-year graduation rate (%)")
        ax.set_title("High schools: freshman on-track vs graduation")
        fig.tight_layout()
        fig.savefig(OUT / "hs_on_track_vs_graduation.png", dpi=150)
        plt.close(fig)


if __name__ == "__main__":
    main()
