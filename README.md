# NYC Housing & Transportation — Data Engineering and Visualization

**Milestone 1 | Winter 2026 | German International University**

This project combines NYC Open Data housing and transportation records at **ZIP code × year** level and presents the results through a Jupyter notebook and an interactive Dash/Plotly dashboard.

## Datasets

| Domain | Dataset | NYC Open Data ID | Source |
|---|---|---|---|
| Housing | Affordable Housing Production by Building | `hg8x-zxpr` | https://data.cityofnewyork.us/d/hg8x-zxpr |
| Transportation | SIRTA Data Crash (serious-injury and fatal crashes) | `xeqp-qz8h` | https://data.cityofnewyork.us/d/xeqp-qz8h |

The integrated file uses the four complete overlapping years **2022–2025**. The supplied integrated dataset contains **748 ZIP-year rows**, representing **187 ZIP codes** across the five NYC boroughs. It contains 142,480 affordable units completed and 10,563 ZIP-coded serious-crash records. These totals were independently reconciled against the supplied cleaned source CSVs by `member6_validation.py`.

> Interpretation note: SIRTA is a serious-injury/fatal-crash dataset, not a register of every traffic collision. The housing source covers HPD-counted affordable housing, not all market-rate construction. Results show associations, not causation.

## Repository structure

The project uses the current root-level layout shown in the team repository (rather than moving files solely to match an earlier proposed layout):

```text
nyc-housing-transport/
├── assets/                         # Dashboard assets / CSS
├── charts/                         # chart_01.py ... chart_12.py
│   ├── chart_11.py                  # Member 6: correlation heatmap
│   └── chart_12.py                  # Member 6: treemap
├── data/
│   ├── raw/                         # Original downloads; do not edit or commit large raw files
│   └── clean/
│       ├── housing_clean.csv
│       ├── transport_clean.csv
│       └── integrated_zip_year.csv
├── notebooks/
│   └── DataEng_Project1.ipynb
├── app.py
├── chart_loader.py
├── config.py
├── search_parser.py
├── story_section.py
├── member6_validation.py
├── requirements.txt
├── .gitignore
└── README.md
```

If the team stores the integrated CSV under `data/integrated/` instead, the validation script supports that location too. The dashboard's `config.py` must point `DATA_PATH` to the actual integrated CSV. Keep `zip_code` as a five-character string when reading CSV files, for example `pd.read_csv(path, dtype={"zip_code": "string"})`; CSV files do not preserve pandas dtypes by themselves.

## Local setup

Use Python 3.10 or newer.

```bash
# 1. Create and activate a virtual environment
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate

# 2. Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# 3. Start the dashboard from the repository root
python app.py
```

Open `http://127.0.0.1:8050` unless the `PORT` environment variable specifies another port.

The existing `app.py` imports `config.py`, `search_parser.py`, and `story_section.py`; those modules must be present in the repository. The `charts/` directory must contain the chart modules. The dashboard chart loader expects each chart module to expose `TITLE`, `QUESTION`, and `build_figure(df, filters)`. Member 6's chart files also expose the course-required `make_chart_11(df)` and `make_chart_12(df)` functions.

## Data validation

Run the Member 6 checks from the repository root after placing the three cleaned CSV files in `data/clean/`:

```bash
python member6_validation.py
python -m pytest -q tests/test_member6_charts.py
```

The script checks the integrated schema, ZIP/year keys, complete four-year grid, borough names, NYC coordinates, non-negative counts, category rules, derived-rate calculations, zero-denominator handling, source-to-integrated conservation of affordable units and serious crashes, and the integrated ZIP universe. It writes:

- `reports/member6_validation/validation_checks.csv`
- `reports/member6_validation/validation_summary.json`
- `reports/member6_validation/final_missingness_profile.png`
- `reports/member6_validation/source_integration_reconciliation.png`
- `reports/member6_validation/integration_source_counts.png`

The final missingness profile is explicitly a **final-state** profile. Before/after cleaning charts belong in the notebook, where raw and cleaned dataframes are available in the top-to-bottom execution flow. Do not label a final-only profile as a before/after comparison.

## Dashboard deployment

For a Render web service:

- **Build command:** `pip install -r requirements.txt`
- **Start command:** `gunicorn app:server`
- Ensure `app.py` exposes `server = app.server` (the supplied app does).
- Configure the app's data path in `config.py` and ensure required CSVs and chart modules are included in the deployment.

**Live dashboard URL:** `ADD_DEPLOYED_URL`  
**GitHub repository:** `ADD_GITHUB_REPOSITORY_URL`

Do not submit these placeholders. Replace them with the actual public/accessible links and test the deployed site in a separate browser or device.

## Chart catalogue

| Chart | Owner | Visualization | Research focus |
|---|---|---|---|
| 01–02 | Member 1 | Housing bar / box plot | Housing production patterns |
| 03–04 | Member 2 | Transport trend / heatmap | Serious-crash patterns |
| 05–06 | Member 3 | Cross-domain scatter / bubble or map | Housing–transport relationship |
| 07–08 | Member 4 | Borough comparison / multi-year trend | Crash burden relative to affordable housing |
| 09–10 | Member 5 | Map overlay / ZIP map | Spatial overlap and distribution |
| 11 | Member 6 | Cross-domain Spearman correlation heatmap | Which housing indicators move with serious-crash outcomes? |
| 12 | Member 6 | Borough × housing-category treemap | How crash burden and fatal-crash share vary by borough and housing activity |

### Member 6 research questions

**RQ11 — Correlation heatmap.** Across ZIP-year observations, which affordable-housing production indicators have the strongest monotonic association with serious crashes and injury outcomes? The supplied data show the strongest pair as projects completed vs. serious crashes (Spearman ρ ≈ 0.620, n = 748). This is an association across ZIP-years, not evidence that housing projects cause crashes.

**RQ12 — Treemap.** How does the serious-crash burden and fatal-crash share vary across boroughs and the dominant affordable-housing activity in each ZIP-year? The treemap sizes each borough/activity segment by serious-crash count and colors it by fatal-crash share. The housing category is assigned from the dominant affordable-unit activity in that ZIP-year; “No completions” means no recorded completed affordable units, not no housing activity of any kind.

## Contributions

Replace the member-ID placeholders and confirm the final contribution notes with each teammate before submission. The table below records the assigned workstreams from the team plan; update it if actual contributions differ.

| Member | Member ID | Data / notebook contribution | Website contribution | Research questions and charts |
|---|---|---|---|---|
| 1 | `ADD_ID` | Housing EDA, cleaning, `housing_clean.csv` | — | Housing RQs; charts 01–02 |
| 2 | `ADD_ID` | Transportation sampling, EDA, cleaning, `transport_clean.csv` | — | Transport RQs; charts 03–04 |
| 3 | `ADD_ID` | ZIP-year integration, post-integration cleaning, data dictionary | — | Cross-domain RQs; charts 05–06 |
| 4 | `ADD_ID` | — | Dash app, filters, Generate Report, chart registry | Cross-domain RQs; charts 07–08 |
| 5 | `ADD_ID` | Story text and prompt/deployment notes | Search mode, CSS, deployment | Spatial RQs; charts 09–10 |
| 6 | `ADD_ID` | Repository, notebook structure, validation plots, README, QA and submission | Chart integration support | Correlation / distribution RQs; charts 11–12 |

## Git workflow

1. Each member works on a separate branch, for example `feat/member-6-validation`.
2. Pull the latest `main` before starting work and before opening a pull request.
3. Avoid editing the same notebook cells at the same time. Agree on notebook ownership and merge notebook changes deliberately.
4. Do not commit `.venv/`, secrets, Jupyter checkpoints, or large raw downloads. Keep cleaned and integrated outputs needed by the app available to the team.
5. Run the notebook top to bottom, run `python member6_validation.py`, and test every chart in the deployed app before submission.

## Known limitations

- Serious-crash counts are not normalized by traffic volume, population, or road-user exposure.
- ZIP codes are postal areas and do not perfectly represent neighborhoods; ZIPs that straddle boroughs receive one majority-vote borough label.
- HPD affordable-housing records do not represent all housing construction.
- Crashes without a usable ZIP are excluded from ZIP-year integration; the integrated crash totals therefore represent ZIP-coded SIRTA records.
- `crashes_per_100_units` and `deeply_affordable_share` are undefined when completed affordable units equal zero. `injuries_per_crash` is undefined when there are no serious crashes.
- Correlation and grouped comparisons are descriptive and cannot establish causation.
