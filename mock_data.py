"""Generate realistic, statistically correlated sample data for dashboard prototyping."""
import numpy as np
import pandas as pd

import config

def create_mock_data(seed: int = 42) -> pd.DataFrame:
    """Return ZIP-code/year data for five NYC boroughs (2022–2025) with realistic variance."""
    rng = np.random.default_rng(seed)
    
    zip_codes_by_borough = {
        "Bronx": ["10451", "10452", "10453", "10454", "10455"],
        "Brooklyn": ["11201", "11203", "11206", "11211", "11215"],
        "Manhattan": ["10001", "10002", "10003", "10009", "10019"],
        "Queens": ["11101", "11354", "11355", "11368", "11432"],
        "Staten Island": ["10301", "10302", "10304", "10305", "10314"],
    }

    # Base modifiers to create realistic geographic disparities
    borough_factor = {
        "Bronx": 0.85, "Brooklyn": 1.25, "Manhattan": 1.80,
        "Queens": 1.10, "Staten Island": 0.60,
    }

    rows = []
    
    for borough, zip_codes in zip_codes_by_borough.items():
        for zip_code in zip_codes:
            # Introduce neighborhood-level variance
            local_factor = borough_factor[borough] * rng.uniform(0.70, 1.30)
            
            # Create a slight upward year-over-year development trend
            for year in config.YEARS:
                year_factor = 1 + (year - 2022) * rng.uniform(0.02, 0.08)
                
                # Base housing metric (e.g., total units)
                housing_base = max(10, rng.normal(120 * local_factor * year_factor, 30))
                
                # Correlate transportation with housing density (more units = more transit/crashes)
                transport_base = housing_base * rng.normal(45, 10)

                rows.append({
                    config.ZIP_COLUMN: zip_code,
                    config.BOROUGH_COLUMN: borough,
                    config.YEAR_COLUMN: year,
                    
                    # Housing Metrics
                    config.HOUSING_METRIC_1_COLUMN: int(housing_base),
                    config.HOUSING_METRIC_2_COLUMN: int(
                        max(0, rng.normal(housing_base * 2.5, 15))
                    ),
                    config.HOUSING_CATEGORY_COLUMN: rng.choice(
                        config.HOUSING_CATEGORIES,
                        p=[0.50, 0.35, 0.15], # Weighted towards common categories
                    ),
                    
                    # Transportation Metrics
                    config.TRANSPORT_METRIC_1_COLUMN: int(transport_base),
                    config.TRANSPORT_METRIC_2_COLUMN: round(
                        max(1.0, rng.normal(15 * local_factor, 3)), 2
                    ),
                    config.TRANSPORT_CATEGORY_COLUMN: rng.choice(
                        config.TRANSPORT_CATEGORIES
                    ),
                })

    return pd.DataFrame(rows, columns=config.EXPECTED_COLUMNS)