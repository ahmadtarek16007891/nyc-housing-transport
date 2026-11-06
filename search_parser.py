"""Search-query parser with keyword extraction."""
import re
from typing import Any, Dict

import config

def parse_query(text: str) -> Dict[str, Any]:
    """Extract a borough, year, and categories from free-text input."""
    query = (text or "").strip().lower()
    parsed = {
        "borough": config.ALL_VALUE,
        "year": [config.ALL_VALUE],
        "housing_category": config.ALL_VALUE,
        "transportation_category": config.ALL_VALUE,
    }

    if not query:
        return parsed

    # 1. Parse Boroughs
    borough_aliases = {
        "bronx": "Bronx", "brooklyn": "Brooklyn",
        "manhattan": "Manhattan", "queens": "Queens",
        "staten island": "Staten Island",
    }
    for alias, borough in borough_aliases.items():
        if re.search(rf"\b{re.escape(alias)}\b", query):
            parsed["borough"] = borough
            break

    # 2. Parse Years (2022-2025)
    found_years = sorted({
        int(value) for value in re.findall(r"\b202[2-5]\b", query)
    })
    if found_years:
        parsed["year"] = found_years

    # 3. Parse Categories via keyword matching
    # Map common search terms to your config's actual category strings
    for category in config.HOUSING_CATEGORIES:
        # Create a simplified slug of the category for matching
        slug = re.sub(r'[^a-z0-9]', '', category.lower())
        if slug in re.sub(r'[^a-z0-9]', '', query):
            parsed["housing_category"] = category
            break
            
    for category in config.TRANSPORT_CATEGORIES:
        slug = re.sub(r'[^a-z0-9]', '', category.lower())
        if slug in re.sub(r'[^a-z0-9]', '', query):
            parsed["transportation_category"] = category
            break

    return parsed