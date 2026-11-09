"""Rule-based search parser (Member 5).

Turns a typed query such as "Brooklyn 2022 new buildings" into dropdown values.

"""
import re

import config

# Words that map to a borough (lowercase). Longest phrases are checked first.
BOROUGH_WORDS = {
    "staten island": "Staten Island",
    "bronx": "Bronx",
    "brooklyn": "Brooklyn",
    "manhattan": "Manhattan",
    "queens": "Queens",
}

# Words that map to the housing category dropdown.
HOUSING_WORDS = {
    "new construction": "New Construction",
    "new buildings": "New Construction",
    "new building": "New Construction",
    "new housing": "New Construction",
    "construction": "New Construction",
    "preservation": "Preservation",
    "preserved": "Preservation",
    "renovation": "Preservation",
    "no completions": "No completions",
    "no housing": "No completions",
}

# Words that map to the transportation category dropdown.
TRANSPORT_WORDS = {
    "fatal": "Fatal crash recorded",
    "deadly": "Fatal crash recorded",
    "death": "Fatal crash recorded",
    "serious injur": "Serious injuries only",
    "injur": "Serious injuries only",
    "no crashes": "No serious crashes",
    "safe": "No serious crashes",
}


def _first_match(text, words):
    """Return the value for the longest keyword found in text, else None."""
    for keyword in sorted(words, key=len, reverse=True):
        # \b at the start so "safe" does not match "unsafe" or "construction" "reconstruction";
        # no \b at the end so "injur" still matches "injuries" and "injured".
        if re.search(r"\b" + re.escape(keyword), text):
            return words[keyword]
    return None


def parse_query(query):
    """Return (filters, recognized_labels).

    filters has the four dropdown keys; unrecognized ones stay at "All".
    An empty query returns the all-default filters (a reset).
    """
    filters = {
        "borough": config.ALL_VALUE,
        "year": [config.ALL_VALUE],
        "housing_category": config.ALL_VALUE,
        "transportation_category": config.ALL_VALUE,
    }
    found = []
    text = (query or "").lower().strip()
    if not text:
        return filters, found

    borough = _first_match(text, BOROUGH_WORDS)
    if borough:
        filters["borough"] = borough
        found.append(borough)

    # Keep only years that exist in the integrated data (2022-2025).
    years = [int(y) for y in re.findall(r"\b(20\d{2})\b", text) if int(y) in config.YEARS]
    if years:
        filters["year"] = sorted(set(years))
        found.extend(str(y) for y in filters["year"])

    housing = _first_match(text, HOUSING_WORDS)
    if housing:
        filters["housing_category"] = housing
        found.append(housing)

    transport = _first_match(text, TRANSPORT_WORDS)
    if transport:
        filters["transportation_category"] = transport
        found.append(transport)

    return filters, found


if __name__ == "__main__":
    tests = ["Brooklyn 2022 new buildings", "queens fatal 2024", "2023", "bronx preservation",
             "pizza", "", "Staten Island 2019", "Manhattan serious injuries 2022 2025"]
    for t in tests:
        print(repr(t), "->", parse_query(t))