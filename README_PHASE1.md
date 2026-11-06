# NYC Housing & Transportation Dashboard — Phase 1

## Assumptions
- The integrated dataset is not ready yet; the app uses deterministic mock data.
- The placeholder schema is defined centrally in `config.py`.
- The chart interface is `TITLE`, `QUESTION`, and `build_figure(df, filters)`.
- The app loads the CSV once at startup. Restart the app after replacing the CSV.
- Search applies parsed values to the dropdowns; charts refresh only after clicking Generate Report.

## Run locally

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:8050.

## Chart interface

Every `charts/chart_XX.py` must expose:

```python
TITLE = "Chart title"
QUESTION = "Research question"

def build_figure(df, filters):
    # df has already been filtered by the app
    # return a plotly.graph_objects.Figure
    ...
```

Do not load the CSV inside chart files. Use `config.py` constants for column names.
The `filters` dictionary contains `borough`, `year`, `housing_category`, and
`transportation_category`.

## Render deployment

1. Push the repository to GitHub.
2. In Render, create a **New Web Service** and connect the repository.
3. Select the Python runtime.
4. Set Build Command to:

   `pip install -r requirements.txt`

5. Set Start Command to:

   `gunicorn app:server`

6. Choose the free instance type if available for your account.
7. Deploy. Render installs dependencies and starts the Dash WSGI server.

The CSV must be committed at `data/clean/integrated_zip_year.csv` for deployment.
If it is absent, the app starts with mock data and displays a banner.

## Phase 1 test checklist

- [ ] App starts with mock data when the integrated CSV is absent.
- [ ] Mock-data banner is visible.
- [ ] Borough dropdown supports All and each borough.
- [ ] Year dropdown supports All and multiple years.
- [ ] Housing category dropdown supports All and each category.
- [ ] Transportation category dropdown supports All and each category.
- [ ] Search recognizes borough names and years.
- [ ] Search changes dropdown values but does not refresh charts automatically.
- [ ] Generate Report refreshes all 12 charts.
- [ ] Combined filters work together.
- [ ] A filter combination with no matching rows shows the empty-results message.
- [ ] Empty results do not crash chart rendering.
- [ ] All 12 chart cards render.
- [ ] Chart 07 visibly plots a housing metric against a transportation metric.
- [ ] Removing or breaking a chart file produces a placeholder instead of crashing the app.
- [ ] Existing `assets/style.css` is not overwritten.
- [ ] App works using `gunicorn app:server`.

## Notes
- `assets/member4_base.css` is a small baseline stylesheet. A teammate can continue
  to own and edit `assets/style.css`; both stylesheets can coexist.
- Chart 12 is a borough-level illustrative map using approximate borough centroids.
  It is not a ZIP-level map and must not be interpreted as precise geographic data.
  If the final integrated dataset includes coordinates or ZIP boundary geometry,
  replace this with a data-grounded geographic visualization in Phase 2.
