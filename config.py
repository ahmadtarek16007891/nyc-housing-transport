"""Central configuration for the NYC Housing & Transportation dashboard.

Phase 1 uses placeholder column names. In Phase 2, update the values in this
file to match the final integrated dataset.
"""
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
DATA_PATH = ROOT_DIR / "data" / "clean" / "integrated_zip_year.csv"
CHARTS_DIR = ROOT_DIR / "charts"

# Placeholder integrated-data schema.
ZIP_COLUMN = "zip_code"
BOROUGH_COLUMN = "borough"
YEAR_COLUMN = "year"

HOUSING_METRIC_1_COLUMN = "housing_metric_1"
HOUSING_METRIC_2_COLUMN = "housing_metric_2"
HOUSING_CATEGORY_COLUMN = "housing_category"

TRANSPORT_METRIC_1_COLUMN = "transport_metric_1"
TRANSPORT_METRIC_2_COLUMN = "transport_metric_2"
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
HOUSING_CATEGORIES = ["New construction", "Renovation", "Affordable housing"]
TRANSPORT_CATEGORIES = ["Subway", "Bus", "Cycling", "Traffic safety"]
