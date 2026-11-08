"""Central configuration for the NYC Housing & Transportation dashboard.

Phase 1 uses placeholder column names. In Phase 2, update the values in this
file to match the final integrated dataset.
"""
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
DATA_PATH = ROOT_DIR / "data" / "clean" / "integrated_zip_year.csv"
CHARTS_DIR = ROOT_DIR / "charts"

# Integrated-data schema (Member 3, see data/clean/data_dictionary.md).
ZIP_COLUMN = "zip_code"
BOROUGH_COLUMN = "borough"
YEAR_COLUMN = "year"

HOUSING_METRIC_1_COLUMN = "total_units"
HOUSING_METRIC_2_COLUMN = "deeply_affordable_units"
HOUSING_CATEGORY_COLUMN = "housing_category"

TRANSPORT_METRIC_1_COLUMN = "crash_count"
TRANSPORT_METRIC_2_COLUMN = "crashes_per_100_units"
TRANSPORT_CATEGORY_COLUMN = "transport_category"

# Central mapping used by the dropdown filters.
FILTER_COLUMNS = {
    "borough": BOROUGH_COLUMN,
    "year": YEAR_COLUMN,
    "housing_category": HOUSING_CATEGORY_COLUMN,
    "transportation_category": TRANSPORT_CATEGORY_COLUMN,
}

ALL_VALUE = "__ALL__"
EXPECTED_COLUMNS = [
    ZIP_COLUMN,
    BOROUGH_COLUMN,
    YEAR_COLUMN,
    HOUSING_METRIC_1_COLUMN,
    HOUSING_METRIC_2_COLUMN,
    HOUSING_CATEGORY_COLUMN,
    TRANSPORT_METRIC_1_COLUMN,
    TRANSPORT_METRIC_2_COLUMN,
    TRANSPORT_CATEGORY_COLUMN,
]

BOROUGHS = ["Bronx", "Brooklyn", "Manhattan", "Queens", "Staten Island"]
YEARS = [2022, 2023, 2024, 2025]
HOUSING_CATEGORIES = ["New Construction", "Preservation", "No completions"]
TRANSPORT_CATEGORIES = ["Fatal crash recorded", "Serious injuries only", "No serious crashes"]
