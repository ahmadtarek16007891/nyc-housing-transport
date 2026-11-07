# Transport cleaning notes (Member 2)

- Dataset: xeqp-qz8h (SIRTA crashes), filter: `crash_date >= '2022-01-01T00:00:00'`
- Rows before: 13,310 | rows after: 13,301
- Years covered: 2022-2026 (latest year may be partial)

## Every filter, drop and assumption
- Sample: xeqp-qz8h filtered with crash_date >= '2022-01-01T00:00:00'; raw rows downloaded = 13,310.
- Dropped 0 rows with no valid crash date (blank rows / unparseable dates).
- Dropped 0 rows with a crash date in the future.
- Borough: 55 rows missing/unrecognised after mapping (labels seen but unmapped: {}).
- ZIP: 44 ZIPs were malformed or outside 10001-11697 and set to missing.
- Coordinates: 0 points at (0,0) or outside the NYC bounding box set to missing.
- ZIP imputed from nearest ZIP centroid (<=1.5 km) for 3,779 rows; 318 stayed missing.
- Borough filled from ZIP for 38 rows.
- Dropped 9 rows with no borough, ZIP or coordinates.
- total_non_severe_injuries: 0 impossible values set to missing; 2171 flagged as IQR outliers and kept.
- total_severe_injuries: 0 impossible values set to missing; 821 flagged as IQR outliers and kept.
- total_fatalities: 0 impossible values set to missing; 1041 flagged as IQR outliers and kept.
- similar_fatalities_severe: 0 impossible values set to missing; 816 flagged as IQR outliers and kept.
- similar_fatalities_all: 11 impossible values set to missing; 2099 flagged as IQR outliers and kept.
- Removed 0 exact duplicate rows.
- No unique id column found: only exact duplicates removed.
- FINAL: 13,310 raw rows -> 13,301 clean rows (9 removed, 0.1%).
