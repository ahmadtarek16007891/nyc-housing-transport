"""Run: python check_charts.py   (sanity numbers behind charts 1, 2, 5)"""
import numpy as np
import pandas as pd
import config

df = pd.read_csv(config.DATA_PATH)

print("== Per-year totals (chart 2) ==")
print(df.groupby("year")[["total_units", "crash_count", "fatal_crashes"]].sum())
print("rows per year:", df.groupby("year").size().to_dict())

per_zip = df.groupby("zip_code").agg(units=("total_units", "sum"), crashes=("crash_count", "sum"))
print("\n== Per-ZIP (charts 1 and 5) ==")
print("ZIPs:", len(per_zip),
      "| zero units in all years:", (per_zip.units == 0).sum(),
      "| zero crashes in all years:", (per_zip.crashes == 0).sum())
tiers = pd.cut(per_zip.units, [-1, 0, 499, float("inf")],
               labels=["No new units", "1-499 units", "500+ units"])
print(tiers.value_counts().to_string())

both = per_zip[(per_zip.units > 0) & (per_zip.crashes > 0)]
print("ZIPs plotted in chart 1:", len(both),
      "| log-log r:", round(np.corrcoef(np.log10(both.units), np.log10(both.crashes))[0, 1], 3))

print("\n== match_source ==")
print(df.match_source.value_counts().to_string())
print("\n== Crash count distribution ==")
print(df.crash_count.describe().to_string())