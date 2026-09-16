# Deliverable 4: Christchurch listings cleaning (points 1 and 2)

## Input and results

Input: `christchurch_listings_2025-10_to_2026-06.csv`, created by Deliverable 3. The supplied README identifies Inside Airbnb as the source, with prices in NZD per night. This run uses the supplied CSV, without downloading replacement data.

- Before: 28,795 listing-month records, 19 columns.
- After: 28,795 listing-month records, 17 columns.
- Rows lost: 0.
- Distinct listing IDs across all months: 4,117.
- Input SHA-256: `2005a2803debdf28fc1ed688dac565944b1dfd67c97f5d8d51879b1e3f7489ce`.
- pandas version used: 3.0.5.

A row describes one listing in one labelled month. Count unique IDs within each month; summing monthly counts counts repeated observations, not unique properties across the whole period.

## Decisions, reasons and consequences

| Decision | Reason | Consequence |
| --- | --- | --- |
| Trim text and standardise blanks | Whitespace can create inconsistent categories. | 0 cells had surrounding whitespace; no rows removed. |
| Check duplicates using listing ID and month | Repeated IDs in different months describe different observations. | 0 exact duplicate rows removed; no conflicting listing-month pairs. |
| Validate latitude | Use numeric values and reject impossible ranges; retain unknown values as missing. | 0 invalid values set to missing; 0 missing after numeric validation, before later filling; no rows removed. |
| Validate longitude | Use numeric values and reject impossible ranges; retain unknown values as missing. | 0 invalid values set to missing; 0 missing after numeric validation, before later filling; no rows removed. |
| Validate price | Use numeric values and reject impossible ranges; retain unknown values as missing. | 0 invalid values set to missing; 10,667 missing after numeric validation, before later filling; no rows removed. |
| Validate reviews_per_month | Use numeric values and reject impossible ranges; retain unknown values as missing. | 0 invalid values set to missing; 2,627 missing after numeric validation, before later filling; no rows removed. |
| Validate minimum_nights | Use numeric values and reject impossible ranges; retain unknown values as missing. | 0 invalid values set to missing; 37 missing after numeric validation, before later filling; no rows removed. |
| Validate number_of_reviews | Use numeric values and reject impossible ranges; retain unknown values as missing. | 0 invalid values set to missing; 0 missing after numeric validation, before later filling; no rows removed. |
| Validate calculated_host_listings_count | Use numeric values and reject impossible ranges; retain unknown values as missing. | 0 invalid values set to missing; 0 missing after numeric validation, before later filling; no rows removed. |
| Validate availability_365 | Use numeric values and reject impossible ranges; retain unknown values as missing. | 0 invalid values set to missing; 0 missing after numeric validation, before later filling; no rows removed. |
| Validate number_of_reviews_ltm | Use numeric values and reject impossible ranges; retain unknown values as missing. | 0 invalid values set to missing; 0 missing after numeric validation, before later filling; no rows removed. |
| Keep missing review dates; fill review rate only for zero-review listings | A listing with no reviews has no last review date. Zero reviews supports a zero observed review rate. | 2,627 review rates filled with 0; 2,627 dates remain missing; 0 invalid dates converted to missing; no rows removed. |
| Flag review dates after the labelled month | Actual scrape dates are unavailable; do not guess corrected months or dates. | 3 records flagged in review_after_month_end and retained for source verification. |
| Retain missing prices and minimum nights | Rows are still useful for listing counts; filling prices would invent rental information. | 10,667 missing prices and 37 missing minimum_nights retained. Price summaries must exclude missing prices and report coverage. |
| Retain high positive prices | An unusually high price is not proof of an error. No arbitrary percentile deletion or capping. | Maximum price 43,654 NZD/night retained; no rows removed. Inspect extremes before using means. |
| Keep IDs as text, preserving host_id exactly | Large identifiers can lose precision when converted to floating point. | 34 host_id values already use scientific notation in the source. Their original digits cannot be recovered here; do not use them for verified host joins without source checks. |
| Drop name, host_name, license | Listing/host names are unnecessary for price and count comparisons; the license column is entirely empty when dropped. | 3 columns removed; no rows removed. IDs, month, city, neighbourhood, room type, coordinates, availability and review measures retained. |

## Price coverage by month

| month_year | records | unique_listings | usable_prices | missing_prices | price_coverage_percent |
| --- | --- | --- | --- | --- | --- |
| 2025-10 | 2991 | 2991 | 2821 | 170 | 94.32 |
| 2025-11 | 3047 | 3047 | 2835 | 212 | 93.04 |
| 2025-12 | 3180 | 3180 | 0 | 3180 | 0.0 |
| 2026-01 | 3057 | 3057 | 0 | 3057 | 0.0 |
| 2026-02 | 3190 | 3190 | 0 | 3190 | 0.0 |
| 2026-03 | 3227 | 3227 | 3059 | 168 | 94.79 |
| 2026-04 | 3273 | 3273 | 3069 | 204 | 93.77 |
| 2026-05 | 3361 | 3361 | 3149 | 212 | 93.69 |
| 2026-06 | 3469 | 3469 | 3195 | 274 | 92.1 |

December 2025, January 2026 and February 2026 contain no prices in the supplied file. Their average or median price is unavailable, not zero. Keeping these records preserves listing counts. Recovering these prices would require checking the original source files. Missing prices can bias comparisons if listings with prices differ from those without prices.

## Missing values before and after

| column | missing_before | missing_after | status |
| --- | --- | --- | --- |
| availability_365 | 0.0 | 0.0 | retained |
| calculated_host_listings_count | 0.0 | 0.0 | retained |
| host_id | 0.0 | 0.0 | retained |
| host_name | 1.0 | — | dropped |
| id | 0.0 | 0.0 | retained |
| last_review | 2627.0 | 2627.0 | retained |
| latitude | 0.0 | 0.0 | retained |
| license | 28795.0 | — | dropped |
| longitude | 0.0 | 0.0 | retained |
| minimum_nights | 37.0 | 37.0 | retained |
| month_year | 0.0 | 0.0 | retained |
| name | 0.0 | — | dropped |
| neighbourhood | 0.0 | 0.0 | retained |
| neighbourhood_group | 0.0 | 0.0 | retained |
| number_of_reviews | 0.0 | 0.0 | retained |
| number_of_reviews_ltm | 0.0 | 0.0 | retained |
| price | 10667.0 | 10667.0 | retained |
| review_after_month_end | — | 0.0 | added |
| reviews_per_month | 2627.0 | 0.0 | retained |
| room_type | 0.0 | 0.0 | retained |

The three removed columns and the added date-quality flag explain the net column change. Remaining missing values are intentional; cleaning does not require every cell to be filled.

## Interpretation and limitations

- Latitude and longitude are retained without rounding. Global coordinate bounds were checked; city membership relies on the supplied Christchurch City label rather than a new boundary check.
- All four observed room types are retained: Entire home/apt, Private room, Shared room and Hotel room. Select appropriate types explicitly for later comparisons.
- Zero availability is retained. A zero value does not identify whether a property is booked or blocked by its host. The dataset supports counts of listed properties; it does not establish housing supply available for long-term rent.
- `review_after_month_end` is True where last_review is later than the end of month_year. Check the original monthly extracts for these records. Do not derive days since review from an assumed common scrape date.
- The supplied README's calculated_host_listings_count definition should be checked: it labels the field as a review count even though the field concerns host listings. No host-based calculation is performed here.
- Airbnb nightly prices and later rental-bond prices need compatible units and property definitions before comparison. No conversion or bond-data processing is included in points 1–2.

## How to rerun

Place `airbnb_deliverable_4.py` beside the original combined CSV. With Python and pandas installed, run:

```bash
python airbnb_deliverable_4.py
```

This creates `cleaned/christchurch_listings_cleaned.csv` and `cleaned/deliverable_4_cleaning_notes.md`. An alternative input and output folder can be supplied:

```bash
python airbnb_deliverable_4.py path/to/input.csv --output-dir cleaned
```

When reloading the output in pandas, use `dtype={"id": "string", "host_id": "string"}` to preserve identifiers. `month_year` is YYYY-MM text; `last_review` is YYYY-MM-DD text with blank values for missing dates. Numeric missing values are exported as blank cells.
