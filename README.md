# NYC Housing & Transportation: Data Engineering and Visualization

**Milestone 1 | Winter 2026 | German International University**

This project combines NYC Open Data housing and transportation records at **ZIP code x year** level. It delivers a Jupyter/Colab notebook (EDA, cleaning, integration, 12 research questions) and an interactive Dash/Plotly website with dropdown filters, a search box, a **Generate Report** button, 12 charts and a story section.

**GitHub repository:** https://github.com/ahmadtarek16007891/nyc-housing-transport
**Live dashboard (Vercel):** https://nyc-housing-transport-six.vercel.app/

## Datasets

| Domain | Dataset | NYC Open Data ID | Source |
|---|---|---|---|
| Housing | Affordable Housing Production by Building | `hg8x-zxpr` | https://data.cityofnewyork.us/d/hg8x-zxpr |
| Transportation | SIRTA Data Crash (serious-injury and fatal crashes) | `xeqp-qz8h` | https://data.cityofnewyork.us/d/xeqp-qz8h |

**Why these two:** both have a ZIP code and a date, so they can be joined without matching individual records. Housing measures new supply; crashes measure severe street risk.

**Integration:** both cleaned files are aggregated to ZIP x year, restricted to the four overlapping full years **2022-2025**, and combined with a full outer join on a complete ZIP x year grid (justification in the notebook). The integrated dataset has **748 ZIP-year rows** for **187 ZIP codes** across the five boroughs, with 142,480 affordable units completed and 10,563 ZIP-coded serious-crash records. These totals are reconciled against the cleaned source files by `member6_validation.py`.

> SIRTA covers serious-injury and fatal crashes, not every collision. The housing data covers HPD-counted affordable housing, not all construction. Results show associations, not causation.

## Repository structure

```text
nyc-housing-transport/
├── app.py                  Dash app: filters, search, Generate Report, story section
├── chart_loader.py         loads chart_01 ... chart_12; a failing chart shows a placeholder
├── config.py               paths and constants (DATA_PATH)
├── search_parser.py        search box query parser
├── story_section.py        story text shown on the site
├── charts/                 chart_01.py ... chart_12.py
├── assets/                 member4_base.css
├── data/
│   ├── raw/                created by the notebook when it downloads the data (git-ignored)
│   └── clean/              housing_clean.csv, transport_clean.csv, integrated_zip_year.csv,
│                           integration_row_log.csv, data_dictionary.md, transport_notes.md
├── notebooks/DataEng_Project1.ipynb
├── reports/member6_validation/   validation plots, checks and summary
├── tests/test_member6_charts.py
├── member6_validation.py
├── requirements.txt
├── README.md
```

Every chart module exposes `TITLE`, `QUESTION` and `build_figure(df, filters)`. Keep `zip_code` a five-character string when reading CSVs, for example `pd.read_csv(path, dtype={"zip_code": str})`.

## Local setup

Use Python 3.10 or newer.

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1          # Windows PowerShell
source .venv/bin/activate           # macOS / Linux
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:8050` (or the port in the `PORT` environment variable).

## Using the website

1. **Dropdown filters:** borough, year (multi-select), housing category and transportation category.
2. **Search mode:** type a query such as `Brooklyn 2022 new buildings`. The search fills the dropdowns; it recognises boroughs, years 2022-2025, housing categories and transport categories. An empty query resets the filters; an unrecognised query shows "No filters recognized".
3. **Generate Report:** click to rebuild all 12 charts and the summary line from the current filters. A selection with no rows shows an empty-state message.
4. **Story section:** question, data and integration, findings, limitations and benefit to NYC.
5. Charts are interactive (hover, zoom, legend filtering).

## Data validation

Run from the repository root:

```bash
python member6_validation.py
python -m pytest -q tests/test_member6_charts.py
```

The script checks the schema, ZIP/year keys, the complete four-year grid, borough names, NYC coordinates, non-negative counts, category rules, derived rates, zero-denominator handling, and conservation of affordable units and serious crashes between the source and integrated files. It writes its outputs to `reports/member6_validation/`. The missingness profile there is a final-state profile; before/after cleaning comparisons are in the notebook.

## Deployment (Vercel)

The live site runs on Vercel and is connected to the GitHub repository, so every push to `main` redeploys it.

1. Import the GitHub repository in Vercel (*Add New > Project*).
2. Vercel installs the packages in `requirements.txt` and serves the Dash app from `app.py`. The Flask server inside Dash is exposed as `server = app.server`.
3. Make sure `data/clean/integrated_zip_year.csv`, `charts/` and `assets/` are committed, because the app reads them at start-up.
4. After each deploy, open the live URL and test the dropdowns, the search box, **Generate Report**, an empty selection and all 12 charts.

Any other host that runs a Python web service (for example Render or Heroku) can use the same code with the start command `gunicorn app:server`.

## Research questions and charts

| Chart | Owner | Chart type | Research question |
|---|---|---|---|
| 01 | Member 1 (Ahmad Tarek) | Scatter, one point per ZIP | RQ1: Do ZIPs that completed more affordable units also have more serious crashes? |
| 02 | Member 1 (Ahmad Tarek) | Yearly trend | RQ2: Do crashes rise or fall in years when more affordable units are completed? |
| 03 | Member 2 (Gaby) | Line by borough | RQ3: How did serious crashes change year to year in each borough, and which boroughs rose most? |
| 04 | Member 2 (Gaby) | Heatmap, borough x year | RQ4: In which borough and year do serious crashes injure the most people per crash? |
| 05 | Member 3 (Nayer) | Box plot by housing tier | RQ5: Do ZIPs that received the most new affordable housing face more serious and fatal crashes than ZIPs that received none? |
| 06 | Member 3 (Nayer) | Map | RQ6: Is new affordable housing being completed in ZIPs where serious crashes are rising or falling? |
| 07 | Member 4 (Ahmed Hossam) | Heatmap, borough x year | RQ7: In which boroughs and years were serious crashes highest relative to affordable housing completed? |
| 08 | Member 4 (Ahmed Hossam) | Bar chart | RQ8: Are serious crashes more likely to be fatal in ZIP-years dominated by new construction than by preservation or no completions? |
| 09 | Member 5 (Tony) | Horizontal bar, top 10 ZIPs | RQ9: Which ZIPs had the most serious crashes relative to the affordable housing they completed? |
| 10 | Member 5 (Tony) | Scatter with trend line | RQ10: In ZIPs where a larger share of new units is deeply affordable, are serious crashes more injurious? |
| 11 | Member 6 (Yasseen) | Spearman correlation heatmap | RQ11: Which housing-production indicators are most strongly associated with serious-crash outcomes? |
| 12 | Member 6 (Yasseen) | Treemap, borough x housing category | RQ12: How do serious-crash burden and fatal-crash share vary by borough and dominant housing activity? |

**Selected findings (2022-2025):** across ZIPs, units completed and serious crashes are strongly associated (Spearman about 0.71, chart 01). Brooklyn holds four of the ten highest crash rates per 100 completed units (chart 09, for example ZIP 11229 at about 79). The deeply affordable share has only a weak link to injuries per crash (Spearman about 0.14, n = 122 ZIPs, chart 10). Across ZIP-years the strongest pair is projects completed versus serious crashes (Spearman about 0.62, n = 748, chart 11). All of these are associations, not evidence of cause.

## Contributions

| Member | Data and notebook contribution | Website contribution | Research questions and charts |
|---|---|---|---|
| 1 - Ahmad Tarek | Housing EDA, cleaning, `housing_clean.csv` | none | RQ1, RQ2; charts 01-02 |
| 2 - Gaby | Transport sampling, EDA, cleaning, `transport_clean.csv` | none | RQ3, RQ4; charts 03-04 |
| 3 - Nayer | ZIP x year integration, post-integration cleaning, `integrated_zip_year.csv`, data dictionary | none | RQ5, RQ6; charts 05-06 |
| 4 - Ahmed Hossam | none | Dash app, data loading, filters, Generate Report, chart loader | RQ7, RQ8; charts 07-08 |
| 5 - Tony | Story text, search-parser tests, prompt log | Search mode (`search_parser.py`), story section (`story_section.py`), CSS, deployment | RQ9, RQ10; charts 09-10 |
| 6 - Yasseen | Repository and notebook structure, validation (`member6_validation.py`, `reports/`), tests, README, QA, prompt log | Chart integration support | RQ11, RQ12; charts 11-12 |

## Git workflow

1. Work on a separate branch per member, for example `feat/member-6-validation`.
2. Pull the latest `main` before starting and before opening a pull request.
3. Agree on notebook ownership to avoid conflicting edits to the same cells.
4. Do not commit `.venv/`, secrets, Jupyter checkpoints or large raw downloads (the raw crash file is git-ignored).
5. Before submission, run the notebook top to bottom, run `python member6_validation.py`, and test every dropdown, the search box, Generate Report, empty results and all 12 charts on the deployed site.

## Known limitations

- Serious-crash counts are not normalised by traffic volume, population or road-user exposure.
- ZIP codes are postal areas, not neighbourhoods; ZIPs that straddle boroughs get one majority-vote borough label.
- HPD affordable-housing records do not cover all housing construction.
- Crashes without a usable ZIP (about 11%) are excluded, so integrated crash totals are ZIP-coded SIRTA records only.
- `crashes_per_100_units` and `deeply_affordable_share` are undefined when completed units are zero; `injuries_per_crash` is undefined when there are no serious crashes.
- Rank-based thresholds (for example 100 units for chart 09, 20 units and 3 crashes for chart 10) exclude small ZIPs.
- Correlations and grouped comparisons are descriptive and cannot establish causation.