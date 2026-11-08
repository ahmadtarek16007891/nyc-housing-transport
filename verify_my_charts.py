"""Run: python verify_my_charts.py   (expected values for charts 7 and 8, all filters = All)"""
import pandas as pd
import config

df = pd.read_csv(config.DATA_PATH, dtype={config.ZIP_COLUMN: str})

print("== Chart 7: crashes per 100 units (ZIP-years with units > 0) ==")
w = df[df.total_units > 0]
g = w.groupby(["borough", "year"]).agg(crashes=("crash_count", "sum"), units=("total_units", "sum"))
g["rate"] = (g.crashes / g.units * 100).round(1)
print(g["rate"].unstack("year").to_string())
print("\nunits behind each cell:")
print(g["units"].unstack("year").to_string())

print("\n== Chart 8: fatal % by housing category (all years) ==")
h = df.groupby("housing_category").agg(crashes=("crash_count", "sum"),
                                       fatal=("fatal_crashes", "sum"), zip_years=("year", "size"))
h["fatal_pct"] = (h.fatal / h.crashes * 100).round(1)
print(h.to_string())