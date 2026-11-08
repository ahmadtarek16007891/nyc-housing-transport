"""Story section shown at the bottom of the dashboard (Member 5).

Numbers come from data/clean/integrated_zip_year.csv (ZIP x year, 2022-2025).
Update the FINDINGS paragraph once teammates send their findings.
"""
from dash import html

STORY_CONTENT = [
    html.H2("The Story: Do Serious Crashes Follow New Affordable Housing?"),
    html.Div(
        [
            html.H3("1. The question"),
            html.P(
                "New York keeps adding affordable homes, but a home is only as good as the streets "
                "around it. We asked whether ZIP codes that complete the most affordable housing also "
                "see more serious-injury and fatal crashes, and whether that changed from 2022 to 2025. "
                "It matters because planners decide where to build and where to fix streets."
            ),
            html.H3("2. The data and how we connected it"),
            html.P(
                "Housing: HPD Affordable Housing Production by Building (hg8x-zxpr). Transportation: "
                "SIRTA crash data (xeqp-qz8h), which only starts in 2022. The two files share no key, so "
                "we aggregated both to ZIP code x year and joined them on a full ZIP-year grid for "
                "2022-2025 (187 ZIPs x 4 years = 748 rows). Crashes missing a ZIP were filled from the "
                "nearest ZIP centre when within 1.5 km; 1,388 crashes (11.6%) still had no ZIP and were "
                "excluded. ZIP-years with no housing or crashes were set to 0, and crash rates are left "
                "empty where no units were completed."
            ),
            html.H3("3. What we found"),
            html.P(
                "Between 2022 and 2025 the ZIPs in our data completed about 142,000 affordable units and "
                "recorded about 10,600 serious or fatal crashes. The Bronx completed the most units "
                "(about 53,000), yet Brooklyn had the most serious crashes (about 3,300). Serious crashes "
                "rose each year, from roughly 2,480 in 2022 to 2,750 in 2025. ZIPs with more completed "
                "units also tend to have more crashes (Spearman correlation about 0.57), but the link is "
                "weak among ZIP-years that actually completed housing (about 0.30). [Add your teammates' "
                "strongest chart findings here.]"
            ),
            html.H3("4. The limits"),
            html.P(
                "Correlation is not causation: bigger ZIPs have more people, streets and housing, so both "
                "counts rise together. SIRTA covers only serious-injury and fatal crashes from 2022, so "
                "this is not all crashes and not a long-term trend. ZIP-level totals hide block-level "
                "differences, and crashes are counted by where they happened, not where residents live. "
                "Housing is counted at completion, so a building's effect on traffic may come later. "
                "Rates per 100 units are unstable when few units were completed."
            ),
            html.H3("5. Why it matters for NYC"),
            html.P(
                "City planners can check street safety before approving large developments and bundle "
                "crosswalks, signals and protected lanes with new buildings. Transportation and safety "
                "agencies can watch ZIPs where housing is growing fast and crashes are high. Housing "
                "advocates can use the ZIP list to press for safer streets near affordable homes."
            ),
        ],
        className="story-content",
    ),
]
