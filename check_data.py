"""Run: python check_data.py
Shows whether the integrated CSV matches what the app and charts expect."""
import pandas as pd
import config

REQUIRED = {
    "app / filters": [config.ZIP_COLUMN, config.BOROUGH_COLUMN, config.YEAR_COLUMN,
                      config.HOUSING_CATEGORY_COLUMN, config.TRANSPORT_CATEGORY_COLUMN],
    "charts 1-5": ["total_units", "crash_count", "fatal_crashes"],
    "chart 6 (map)": ["latitude", "longitude"],
    "config metrics": [config.HOUSING_METRIC_2_COLUMN, config.TRANSPORT_METRIC_2_COLUMN],
}

df = pd.read_csv(config.DATA_PATH, low_memory=False)
print("shape:", df.shape, "\n")
print(df.dtypes.to_string(), "\n")
print(df.head(5).to_string(), "\n")

for group, cols in REQUIRED.items():
    missing = [c for c in cols if c not in df.columns]
    print(f"{group}: {'OK' if not missing else 'MISSING -> ' + str(missing)}")

if config.YEAR_COLUMN in df.columns:
    print("\nyears:", sorted(df[config.YEAR_COLUMN].dropna().unique()))
    
if config.BOROUGH_COLUMN in df.columns:
    print("boroughs:", df[config.BOROUGH_COLUMN].dropna().unique())

if {config.ZIP_COLUMN, config.YEAR_COLUMN} <= set(df.columns):
    print("duplicate ZIP+year rows:", df.duplicated([config.ZIP_COLUMN, config.YEAR_COLUMN]).sum())
print("\nnull counts:\n", df.isna().sum()[lambda s: s > 0].to_string())

for col in (config.HOUSING_CATEGORY_COLUMN, config.TRANSPORT_CATEGORY_COLUMN):
    if col in df.columns:
        print(f"\n{col} values:\n", df[col].value_counts(dropna=False).to_string())