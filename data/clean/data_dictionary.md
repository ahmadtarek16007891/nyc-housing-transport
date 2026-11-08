# Data dictionary: `integrated_zip_year.csv` (Member 3)

One row per **NYC ZIP code x year**, 2022-2025. 187 ZIPs x 4 years = **748 rows, 27 columns**.
Built in `notebooks/member3_integration.ipynb` from `housing_clean.csv` (hg8x-zxpr) and `transport_clean.csv` (xeqp-qz8h).

**Key:** `zip_code` + `year` (unique). **Join:** full outer join on a complete ZIP x year grid; missing counts = 0.
**Years:** 2022-2025 only (SIRTA starts 2022; 2026 dropped because both files stop on 2026-06-30).

## Keys and geography
| Column | Type | Description |
|---|---|---|
| `zip_code` | string (5 digits) | NYC ZIP code (10001-11697). Read with `dtype={'zip_code': str}` |
| `borough` | category | Bronx, Brooklyn, Manhattan, Queens, Staten Island. Majority label across both files (15 border ZIPs had mixed labels) |
| `year` | int | 2022, 2023, 2024, 2025 |
| `latitude`, `longitude` | float | ZIP centre: mean location of all buildings and crashes in that ZIP. Same for every year |

## Housing (Affordable Housing Production by Building), by `completion_year`
| Column | Type | Description |
|---|---|---|
| `buildings_completed` | int | Buildings completed in the ZIP that year |
| `projects_completed` | int | Distinct HPD projects with a building completed |
| `total_units` | int | All units in completed buildings (main housing metric) |
| `new_construction_units` | int | Units in New Construction buildings |
| `preservation_units` | int | Units in Preservation buildings |
| `deeply_affordable_units` | int | Extremely low + very low income units (up to 50% AMI) |
| `low_income_units` | int | Low income units (51-80% AMI) |
| `units_started` | int | Units in buildings whose project **started** that year (includes unfinished projects) |
| `housing_category` | category | `New Construction` / `Preservation` (type with most units) / `No completions` |

## Transportation (SIRTA serious-injury and fatal crashes)
| Column | Type | Description |
|---|---|---|
| `crash_count` | int | Serious-injury or fatal crashes in the ZIP that year (main transport metric) |
| `fatal_crashes` | int | Crashes with at least 1 fatality |
| `fatalities` | int | Total people killed |
| `severe_injuries` | int | Total severe injuries |
| `non_severe_injuries` | int | Total non-severe injuries |
| `transport_category` | category | `Fatal crash recorded` / `Serious injuries only` / `No serious crashes` |

## Derived (cross-domain)
| Column | Type | Description |
|---|---|---|
| `crashes_per_100_units` | float | `crash_count / total_units * 100`. **NaN when total_units = 0** (undefined, not 0) |
| `deeply_affordable_share` | float | `deeply_affordable_units / total_units` (0-1). NaN when no units |
| `injuries_per_crash` | float | (severe + non-severe injuries) / crash_count. NaN when no crashes |

## Quality flags (rows are kept; filter them in charts if needed)
| Column | Type | Description |
|---|---|---|
| `match_source` | category | `both` (390), `transport only` (324), `housing only` (1), `neither (grid fill)` (33) |
| `flag_rate_outlier` | bool | `crashes_per_100_units` above IQR fence (67.5): 43 rows |
| `flag_small_unit_base` | bool | 1-19 units completed, so the rate is unstable: 50 rows |
| `flag_units_outlier` | bool | `total_units` above IQR fence (1,081): 21 very large ZIP-years |

## Totals check (before = after integration)
- Units completed 2022-2025: **142,480**
- Crashes 2022-2025 with a ZIP: **10,563** (1,388 crashes, 11.6%, had no ZIP and are excluded)

## `config.py` mapping
```python
HOUSING_METRIC_1_COLUMN = "total_units"
HOUSING_METRIC_2_COLUMN = "deeply_affordable_units"
HOUSING_CATEGORY_COLUMN = "housing_category"
TRANSPORT_METRIC_1_COLUMN = "crash_count"
TRANSPORT_METRIC_2_COLUMN = "crashes_per_100_units"
TRANSPORT_CATEGORY_COLUMN = "transport_category"
HOUSING_CATEGORIES = ["New Construction", "Preservation", "No completions"]
TRANSPORT_CATEGORIES = ["Fatal crash recorded", "Serious injuries only", "No serious crashes"]
```
