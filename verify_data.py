"""Run: python verify_data.py
Independent checks on the integrated CSV + expected numbers to compare with the dashboard."""
import pandas as pd
import config

df = pd.read_csv(config.DATA_PATH, dtype={config.ZIP_COLUMN: str})
problems = []


def check(name, bad):
    n = int(bad.sum())
    print(f"{'OK    ' if n == 0 else 'FAIL  '}{name}" + ("" if n == 0 else f"  ({n} rows)"))
    if n:
        problems.append(name)


zip_num = pd.to_numeric(df[config.ZIP_COLUMN], errors="coerce")
print("== Structure ==")
check("ZIP is 5 digits", ~df[config.ZIP_COLUMN].str.fullmatch(r"\d{5}"))
check("ZIP in NYC range", ~zip_num.between(10001, 11697))
check("no duplicate ZIP+year", df.duplicated([config.ZIP_COLUMN, "year"]))
check("every ZIP has all 4 years", df.groupby(config.ZIP_COLUMN)["year"].transform("count") != 4)
check("lat/long inside NYC", ~(df.latitude.between(40.45, 40.95) & df.longitude.between(-74.30, -73.65)))

print("\n== Values ==")
count_cols = ["total_units", "new_construction_units", "preservation_units", "deeply_affordable_units",
              "crash_count", "fatal_crashes", "fatalities", "severe_injuries", "non_severe_injuries"]
check("no negative counts", (df[count_cols] < 0).any(axis=1))
check("new + preservation = total units", df.new_construction_units + df.preservation_units != df.total_units)
check("deeply affordable <= total units", df.deeply_affordable_units > df.total_units)
check("fatal crashes <= crashes", df.fatal_crashes > df.crash_count)
check("fatalities >= fatal crashes", df.fatalities < df.fatal_crashes)

print("\n== Derived columns recomputed ==")
has_units, has_crash = df.total_units > 0, df.crash_count > 0
rate = df.crash_count / df.total_units.where(has_units) * 100
check("crashes_per_100_units correct", has_units & ((rate - df.crashes_per_100_units).abs() > 0.011))
check("crashes_per_100_units null only when 0 units", df.crashes_per_100_units.isna() == has_units)
inj = (df.severe_injuries + df.non_severe_injuries) / df.crash_count.where(has_crash)
check("injuries_per_crash correct", has_crash & ((inj - df.injuries_per_crash).abs() > 0.011))
check("injuries_per_crash null only when 0 crashes", df.injuries_per_crash.isna() == has_crash)
share = df.deeply_affordable_units / df.total_units.where(has_units)
check("deeply_affordable_share correct", has_units & ((share - df.deeply_affordable_share).abs() > 0.0011))

print("\n== Categories ==")
check("'No completions' <=> 0 units", (df.housing_category == "No completions") == has_units)
check("'No serious crashes' <=> 0 crashes", (df.transport_category == "No serious crashes") == has_crash)
check("'Fatal crash recorded' <=> fatal_crashes > 0",
      (df.transport_category == "Fatal crash recorded") != (df.fatal_crashes > 0))

print("\n== Borough vs ZIP prefix (REVIEW, not automatic fails) ==")
prefixes = {"Manhattan": ("100", "101", "102"), "Staten Island": ("103",), "Bronx": ("104",),
            "Brooklyn": ("112",), "Queens": ("110", "111", "113", "114", "116")}
odd = df[~df.apply(lambda r: r[config.ZIP_COLUMN].startswith(prefixes[r.borough]), axis=1)]
print("ZIPs to eyeball:", sorted(odd[config.ZIP_COLUMN].unique()) or "none")

print("\n== Expected dashboard summary lines (compare with 'Showing ... records') ==")
combos = [
    ("All data", {}),
    ("Brooklyn", {"borough": "Brooklyn"}),
    ("Brooklyn + 2022", {"borough": "Brooklyn", "years": [2022]}),
    ("2022 + 2023", {"years": [2022, 2023]}),
    ("Queens + 2024 + New Construction", {"borough": "Queens", "years": [2024], "housing": "New Construction"}),
    ("Bronx + Fatal crash recorded", {"borough": "Bronx", "transport": "Fatal crash recorded"}),
    ("Staten Island + 2025 + No serious crashes",
     {"borough": "Staten Island", "years": [2025], "transport": "No serious crashes"}),
]
for label, f in combos:
    d = df
    if "borough" in f: d = d[d.borough == f["borough"]]
    if "years" in f: d = d[d.year.isin(f["years"])]
    if "housing" in f: d = d[d.housing_category == f["housing"]]
    if "transport" in f: d = d[d.transport_category == f["transport"]]
    print(f"{label:45s} -> Showing {len(d):,} ZIP/year records across {d[config.ZIP_COLUMN].nunique():,} NYC ZIP codes.")

print("\n== Numbers behind the new charts 3 and 4 (all years) ==")
print(df.groupby("borough")[["new_construction_units", "preservation_units"]].sum())
g = df.groupby("borough")[["crash_count", "fatal_crashes"]].sum()
g["fatal_pct"] = (g.fatal_crashes / g.crash_count * 100).round(1)
print(g)

print("\nRESULT:", "all checks passed" if not problems else f"{len(problems)} check(s) failed: {problems}")