"""Member 6: reproducible validation of the cleaned and integrated project data.

Run from the repository root:
    python member6_validation.py

The script checks the real CSV files, verifies conservation of housing units and
SIRTA crash records through ZIP-year integration, and saves a CSV/JSON report
plus diagnostic plots under reports/member6_validation/.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

YEARS = {2022, 2023, 2024, 2025}
BOROUGHS = {"Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"}
NYC_ZIP_MIN, NYC_ZIP_MAX = 10001, 11697
LAT_MIN, LAT_MAX = 40.49, 40.92
LON_MIN, LON_MAX = -74.27, -73.68

INTEGRATED_REQUIRED = {
    "zip_code", "borough", "year", "latitude", "longitude",
    "buildings_completed", "projects_completed", "total_units",
    "new_construction_units", "preservation_units", "deeply_affordable_units",
    "low_income_units", "units_started", "housing_category", "crash_count",
    "fatal_crashes", "fatalities", "severe_injuries", "non_severe_injuries",
    "transport_category", "crashes_per_100_units", "deeply_affordable_share",
    "injuries_per_crash", "match_source", "flag_rate_outlier",
    "flag_small_unit_base", "flag_units_outlier",
}


def find_file(root: Path, filename: str) -> Path:
    """Find a project CSV in the actual or planned folder layout."""
    candidates = [
        root / "data" / "clean" / filename,
        root / "data" / "integrated" / filename,
        root / filename,
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    searched = "\n".join(str(path) for path in candidates)
    raise FileNotFoundError(f"Could not find {filename}. Checked:\n{searched}")


def normalize_zip(series: pd.Series) -> pd.Series:
    """Normalize NYC ZIP values to five-character strings and reject invalid ZIPs."""
    digits = (
        series.astype("string")
        .str.strip()
        .str.replace(r"\.0$", "", regex=True)
        .str.extract(r"^(\d{5})$", expand=False)
    )
    numeric = pd.to_numeric(digits, errors="coerce")
    return digits.where(numeric.between(NYC_ZIP_MIN, NYC_ZIP_MAX))


def add_check(
    checks: List[Dict[str, Any]], name: str, passed: bool, detail: str
) -> None:
    checks.append({"check": name, "passed": bool(passed), "detail": detail})


def _same_rounded_values(
    actual: pd.Series, expected: pd.Series, tolerance: float
) -> bool:
    actual_numeric = pd.to_numeric(actual, errors="coerce")
    expected_numeric = pd.to_numeric(expected, errors="coerce")
    if not actual_numeric.isna().equals(expected_numeric.isna()):
        return False
    valid = actual_numeric.notna()
    if not valid.any():
        return True
    return bool(
        np.allclose(
            actual_numeric[valid].to_numpy(dtype=float),
            expected_numeric[valid].to_numpy(dtype=float),
            atol=tolerance,
            rtol=0,
            equal_nan=True,
        )
    )


def validate_data(
    housing: pd.DataFrame,
    transport: pd.DataFrame,
    integrated: pd.DataFrame,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    checks: List[Dict[str, Any]] = []

    missing_columns = sorted(INTEGRATED_REQUIRED.difference(integrated.columns))
    add_check(
        checks,
        "Integrated schema contains all required fields",
        not missing_columns,
        "Missing: " + (", ".join(missing_columns) if missing_columns else "none"),
    )
    if missing_columns:
        raise ValueError("Integrated dataset is missing required columns: " + ", ".join(missing_columns))

    df = integrated.copy()
    df["zip_code"] = normalize_zip(df["zip_code"])
    df["year"] = pd.to_numeric(df["year"], errors="coerce")

    expected_boroughs = set(df["borough"].dropna().astype(str).unique())
    add_check(
        checks,
        "Borough labels use the agreed five names",
        expected_boroughs == BOROUGHS,
        f"Found: {sorted(expected_boroughs)}",
    )

    year_values = set(df["year"].dropna().astype(int).unique())
    add_check(
        checks,
        "Integrated data covers the four complete years 2022-2025",
        year_values == YEARS,
        f"Found: {sorted(year_values)}",
    )

    zip_count = int(df["zip_code"].nunique(dropna=True))
    year_count = int(df["year"].nunique(dropna=True))
    unique_keys = not df.duplicated(["zip_code", "year"]).any()
    full_grid = len(df) == zip_count * year_count and df[["zip_code", "year"]].notna().all().all()
    add_check(
        checks,
        "One row per ZIP-year with no duplicate keys",
        unique_keys and full_grid,
        f"Rows={len(df):,}; ZIPs={zip_count:,}; years={year_count}; expected grid={zip_count * year_count:,}",
    )

    add_check(
        checks,
        "ZIP codes are valid five-character NYC ZIP strings",
        df["zip_code"].notna().all() and df["zip_code"].str.fullmatch(r"\d{5}").all(),
        f"Missing/invalid ZIPs: {int(df['zip_code'].isna().sum())}",
    )

    count_columns = [
        "buildings_completed", "projects_completed", "total_units",
        "new_construction_units", "preservation_units", "deeply_affordable_units",
        "low_income_units", "units_started", "crash_count", "fatal_crashes",
        "fatalities", "severe_injuries", "non_severe_injuries",
    ]
    negative_counts = {
        column: int((pd.to_numeric(df[column], errors="coerce") < 0).sum())
        for column in count_columns
    }
    add_check(
        checks,
        "Count metrics contain no negative values",
        all(count == 0 for count in negative_counts.values()),
        f"Negative values by column: {negative_counts}",
    )

    coordinate_valid = (
        df["latitude"].between(LAT_MIN, LAT_MAX).all()
        and df["longitude"].between(LON_MIN, LON_MAX).all()
    )
    add_check(
        checks,
        "ZIP centroids fall within the NYC coordinate bounds",
        coordinate_valid,
        f"Latitude range={df['latitude'].min():.5f} to {df['latitude'].max():.5f}; "
        f"longitude range={df['longitude'].min():.5f} to {df['longitude'].max():.5f}",
    )

    units_reconcile = (
        df["new_construction_units"] + df["preservation_units"]
    ).equals(df["total_units"])
    add_check(
        checks,
        "New-construction and preservation units sum to total units",
        units_reconcile,
        f"Maximum absolute difference={int((df['new_construction_units'] + df['preservation_units'] - df['total_units']).abs().max())}",
    )

    fatal_counts_valid = (
        (df["fatal_crashes"] <= df["crash_count"]).all()
        and (df["fatalities"] >= df["fatal_crashes"]).all()
    )
    add_check(
        checks,
        "Fatal crash and fatality counts are logically consistent",
        fatal_counts_valid,
        "Requires fatal_crashes <= crash_count and fatalities >= fatal_crashes for every ZIP-year.",
    )

    expected_housing_category = np.select(
        [
            df["total_units"] == 0,
            df["new_construction_units"] >= df["preservation_units"],
        ],
        ["No completions", "New Construction"],
        default="Preservation",
    )
    add_check(
        checks,
        "Housing category matches the documented dominant-activity rule",
        bool((expected_housing_category == df["housing_category"].astype(str)).all()),
        "Zero units -> No completions; otherwise the larger unit type determines the label.",
    )

    expected_transport_category = np.select(
        [df["fatal_crashes"] > 0, df["crash_count"] > 0],
        ["Fatal crash recorded", "Serious injuries only"],
        default="No serious crashes",
    )
    add_check(
        checks,
        "Transportation category matches the documented severity rule",
        bool((expected_transport_category == df["transport_category"].astype(str)).all()),
        "Fatal crash -> Fatal crash recorded; other serious crashes -> Serious injuries only; otherwise none.",
    )

    units_denominator = df["total_units"].replace(0, np.nan)
    crash_denominator = df["crash_count"].replace(0, np.nan)
    expected_crashes_per_100 = (df["crash_count"] / units_denominator * 100).round(2)
    expected_affordable_share = (df["deeply_affordable_units"] / units_denominator).round(3)
    expected_injuries_per_crash = (
        (df["severe_injuries"] + df["non_severe_injuries"])
        / crash_denominator
    ).round(2)

    add_check(
        checks,
        "crashes_per_100_units reproduces from its numerator and denominator",
        _same_rounded_values(df["crashes_per_100_units"], expected_crashes_per_100, 0.011),
        "Recomputed as crash_count / total_units * 100, rounded to two decimals.",
    )
    add_check(
        checks,
        "deeply_affordable_share reproduces from its numerator and denominator",
        _same_rounded_values(df["deeply_affordable_share"], expected_affordable_share, 0.00051),
        "Recomputed as deeply_affordable_units / total_units, rounded to three decimals.",
    )
    add_check(
        checks,
        "injuries_per_crash reproduces from its numerator and denominator",
        _same_rounded_values(df["injuries_per_crash"], expected_injuries_per_crash, 0.011),
        "Recomputed as (severe + non-severe injuries) / crash_count, rounded to two decimals.",
    )

    add_check(
        checks,
        "Zero denominators remain undefined in derived rates",
        (
            df.loc[df["total_units"] == 0, "crashes_per_100_units"].isna().all()
            and df.loc[df["total_units"] == 0, "deeply_affordable_share"].isna().all()
            and df.loc[df["crash_count"] == 0, "injuries_per_crash"].isna().all()
        ),
        "Rate values are missing when their denominator is zero, not falsely filled with zero.",
    )

    # Reconcile source records with the final table. The housing ZIP universe
    # includes projects started in the year even when they are not yet complete.
    h = housing.copy()
    if not {"postcode", "completion_year", "start_year", "total_units"}.issubset(h.columns):
        add_check(checks, "Housing source has required reconciliation fields", False,
                  "Need postcode, completion_year, start_year and total_units.")
        housing_done = housing_started = pd.DataFrame()
    else:
        h["zip_norm"] = normalize_zip(h["postcode"])
        h["completion_year_num"] = pd.to_numeric(h["completion_year"], errors="coerce")
        h["start_year_num"] = pd.to_numeric(h["start_year"], errors="coerce")
        housing_done = h[
            h["completion_year_num"].isin(YEARS) & h["zip_norm"].notna()
        ].copy()
        housing_started = h[
            h["start_year_num"].isin(YEARS) & h["zip_norm"].notna()
        ].copy()
        source_units = pd.to_numeric(housing_done["total_units"], errors="coerce").sum()
        integrated_units = pd.to_numeric(df["total_units"], errors="coerce").sum()
        add_check(
            checks,
            "Housing units are conserved through ZIP-year aggregation",
            int(source_units) == int(integrated_units),
            f"Source completed buildings: {len(housing_done):,}; source units={int(source_units):,}; integrated units={int(integrated_units):,}.",
        )

    t = transport.copy()
    if not {"zip_code", "year", "open_data_crash_id"}.issubset(t.columns):
        add_check(checks, "Transportation source has required reconciliation fields", False,
                  "Need zip_code, year and open_data_crash_id.")
        transport_with_zip = pd.DataFrame()
    else:
        t["zip_norm"] = normalize_zip(t["zip_code"])
        t["year_num"] = pd.to_numeric(t["year"], errors="coerce")
        transport_with_zip = t[
            t["year_num"].isin(YEARS) & t["zip_norm"].notna()
        ].copy()
        source_crashes = transport_with_zip["open_data_crash_id"].nunique()
        integrated_crashes = int(pd.to_numeric(df["crash_count"], errors="coerce").sum())
        add_check(
            checks,
            "SIRTA crash records with ZIPs are conserved through ZIP-year aggregation",
            int(source_crashes) == integrated_crashes,
            f"Source crashes with valid ZIP: {source_crashes:,}; integrated crash_count: {integrated_crashes:,}.",
        )

    if not housing_done.empty and not housing_started.empty and not transport_with_zip.empty:
        source_zip_universe = (
            set(housing_done["zip_norm"].dropna())
            | set(housing_started["zip_norm"].dropna())
            | set(transport_with_zip["zip_norm"].dropna())
        )
        integrated_zip_universe = set(df["zip_code"].dropna())
        add_check(
            checks,
            "Integrated ZIP universe matches the union of both source datasets",
            source_zip_universe == integrated_zip_universe,
            f"Source union={len(source_zip_universe):,}; integrated ZIPs={len(integrated_zip_universe):,}.",
        )

    match_sources = sorted(df["match_source"].dropna().astype(str).unique())
    allowed_match_sources = {"both", "housing only", "transport only", "neither (grid fill)"}
    add_check(
        checks,
        "Integration provenance labels use the documented values",
        set(match_sources).issubset(allowed_match_sources),
        f"Found: {match_sources}",
    )

    summary = {
        "integrated_rows": int(len(df)),
        "zip_codes": int(zip_count),
        "years": sorted(int(value) for value in year_values),
        "boroughs": sorted(str(value) for value in expected_boroughs),
        "total_completed_units": int(pd.to_numeric(df["total_units"], errors="coerce").sum()),
        "serious_crashes_with_zip": int(pd.to_numeric(df["crash_count"], errors="coerce").sum()),
        "fatal_crashes": int(pd.to_numeric(df["fatal_crashes"], errors="coerce").sum()),
        "fatalities": int(pd.to_numeric(df["fatalities"], errors="coerce").sum()),
        "null_rates": {
            column: round(float(df[column].isna().mean() * 100), 2)
            for column in ["crashes_per_100_units", "deeply_affordable_share", "injuries_per_crash"]
        },
        "housing_clean_rows": int(len(housing)),
        "transport_clean_rows": int(len(transport)),
    }
    return checks, summary


def make_diagnostic_plots(
    housing: pd.DataFrame,
    transport: pd.DataFrame,
    integrated: pd.DataFrame,
    output_dir: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    # Final null profile: this is deliberately labelled as a final-state profile,
    # not a before/after comparison (raw files are not always committed).
    frames = {
        "Housing clean": housing,
        "Transport clean": transport,
        "Integrated": integrated,
    }
    fig, axes = plt.subplots(1, 3, figsize=(17, 6))
    for axis, (name, frame) in zip(axes, frames.items()):
        null_pct = (frame.isna().mean() * 100).sort_values(ascending=False)
        null_pct = null_pct[null_pct > 0].head(12).sort_values()
        if null_pct.empty:
            axis.text(0.5, 0.5, "No missing values", ha="center", va="center")
        else:
            null_pct.plot(kind="barh", ax=axis)
        axis.set_title(name)
        axis.set_xlabel("Missing values (%)")
        axis.set_ylabel("Column")
    fig.suptitle("Final-state missingness profile (not a before/after comparison)")
    fig.tight_layout()
    fig.savefig(output_dir / "final_missingness_profile.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    # Verify conservation visually: totals must match the independent source sums.
    h = housing.copy()
    h["zip_norm"] = normalize_zip(h["postcode"])
    h["completion_year_num"] = pd.to_numeric(h["completion_year"], errors="coerce")
    h_done = h[h["completion_year_num"].isin(YEARS) & h["zip_norm"].notna()]
    source_units = int(pd.to_numeric(h_done["total_units"], errors="coerce").sum())
    integrated_units = int(pd.to_numeric(integrated["total_units"], errors="coerce").sum())

    t = transport.copy()
    t["zip_norm"] = normalize_zip(t["zip_code"])
    t["year_num"] = pd.to_numeric(t["year"], errors="coerce")
    t_zip = t[t["year_num"].isin(YEARS) & t["zip_norm"].notna()]
    source_crashes = int(t_zip["open_data_crash_id"].nunique())
    integrated_crashes = int(pd.to_numeric(integrated["crash_count"], errors="coerce").sum())

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    labels = ["Source rows/sum", "Integrated sum"]
    axes[0].bar(labels, [source_units, integrated_units])
    axes[0].set_title("Affordable units conserved")
    axes[0].set_ylabel("Completed units")
    axes[1].bar(labels, [source_crashes, integrated_crashes])
    axes[1].set_title("ZIP-coded serious crashes conserved")
    axes[1].set_ylabel("Serious-crash records")
    for axis in axes:
        axis.tick_params(axis="x", rotation=12)
    fig.suptitle("Source-to-integrated total reconciliation")
    fig.tight_layout()
    fig.savefig(output_dir / "source_integration_reconciliation.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    # Integration provenance counts provide a direct view of the outer join.
    source_counts = integrated["match_source"].astype(str).value_counts()
    fig, axis = plt.subplots(figsize=(8, 4.5))
    source_counts.sort_values().plot(kind="barh", ax=axis)
    axis.set_title("ZIP-year records by integration source")
    axis.set_xlabel("ZIP-year records")
    axis.set_ylabel("Source")
    fig.tight_layout()
    fig.savefig(output_dir / "integration_source_counts.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent,
                        help="Project root (defaults to this script's parent directory).")
    parser.add_argument("--output-dir", type=Path, default=None,
                        help="Output directory (default: reports/member6_validation).")
    args = parser.parse_args()

    root = args.root.resolve()
    output_dir = args.output_dir or (root / "reports" / "member6_validation")
    housing_path = find_file(root, "housing_clean.csv")
    transport_path = find_file(root, "transport_clean.csv")
    integrated_path = find_file(root, "integrated_zip_year.csv")

    housing = pd.read_csv(housing_path, dtype={"postcode": "string"}, low_memory=False)
    transport = pd.read_csv(transport_path, dtype={"zip_code": "string"}, low_memory=False)
    integrated = pd.read_csv(integrated_path, dtype={"zip_code": "string"}, low_memory=False)

    checks, summary = validate_data(housing, transport, integrated)
    output_dir.mkdir(parents=True, exist_ok=True)
    checks_df = pd.DataFrame(checks)
    checks_df.to_csv(output_dir / "validation_checks.csv", index=False)
    with (output_dir / "validation_summary.json").open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2)
    make_diagnostic_plots(housing, transport, integrated, output_dir)

    passed = int(checks_df["passed"].sum())
    failed = int((~checks_df["passed"]).sum())
    print(f"Member 6 validation: {passed} passed, {failed} failed.")
    print(json.dumps(summary, indent=2))
    print(f"Reports saved to: {output_dir}")
    if failed:
        print("Failed checks:")
        print(checks_df.loc[~checks_df["passed"]].to_string(index=False))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
