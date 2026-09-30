# Design Principles Document — Christchurch Airbnb & Long-Term Rental Pipeline

**AI used to help draft this document:** Claude (Anthropic), Claude Sonnet 4.6, via claude.ai. The AI was used to help structure and write up this document, based on the actual content of the Deliverable 3 combine/prepare script, `changed_airbnb_deliverable_4.py`, `changed_rental_bond.py`, `join_datasets.py`, and `christchurch_airbnb_rental_analysis.py`, as reviewed in conversation. The design decisions themselves originate from the project code; this document describes and explains them.

This document treats "the pipeline" as the full sequence of scripts that turns the raw monthly Airbnb export files and the raw tenancy-bond file into the final analysis outputs: **Deliverable 3 (combine & prepare) → Deliverable 4 (clean) → Deliverable 5 (join & analyse)**.

---

## 1. Inputs to the pipeline

| Stage | Input file(s) | Format / notes |
| --- | --- | --- |
| Deliverable 3 | Nine monthly Airbnb listing export files (October 2025 – June 2026), one per month, stored in the project's raw-data folder | Raw Inside Airbnb monthly snapshots, not limited to Christchurch. |
| Deliverable 4 — `changed_airbnb_deliverable_4.py` | `christchurch_listings_2025-10_to_2026-06.csv` (produced by Deliverable 3) | Combined, Christchurch-only, listing-month records. Read with `dtype="string"` so no column is implicitly coerced before validation. |
| Deliverable 4 — `changed_rental_bond.py` | `Detailed-Quarterly-Tenancy-Q1-2020-Q3-2026.csv` | Quarterly tenancy bond data (NZ-wide, multiple years). Filtered down to only the quarters relevant to the Airbnb comparison window. |
| Deliverable 5 — `join_datasets.py` | `christchurch_listings_cleaned.csv` (from Deliverable 4) and `rental_bond_cleaned_filtered.csv` (from Deliverable 4) | The two cleaned datasets, joined on `area_code`/`Location Id` and `TimeFrame`. |
| Deliverable 5 — `christchurch_airbnb_rental_analysis.py` | `christchurch_airbnb_rental_joined.csv` (from `join_datasets.py`), plus `rental_bond_cleaned_filtered.csv` loaded again directly for the property-count comparison | The joined dataset for the price-gap analysis; the cleaned bond dataset again for counting long-term rental properties by location. |

Every script in the pipeline takes its input path as an optional command-line argument or resolves it relative to its own file location, rather than depending on a hard-coded absolute path or a specific working directory.

## 2. Outputs from the pipeline

| Stage | Output(s) |
| --- | --- |
| Deliverable 3 | `christchurch_listings_2025-10_to_2026-06.csv` (the combined, Christchurch-only, processed dataset — saved only after all processing steps are complete). Summary files: `missing_values_summary.csv`, `numerical_summary.csv`, `categorical_summary.csv`, `category_counts.csv`. Visualisations: `christchurch_price_histogram.png`, `days_since_last_review_histogram.png`. |
| Deliverable 4 — Airbnb | `cleaned/christchurch_listings_cleaned.csv` and an auto-generated `cleaned/deliverable_4_cleaning_notes.md` report documenting every cleaning decision, its reasoning, and its consequence. |
| Deliverable 4 — rental bond | `rental_bond_cleaned_filtered.csv` — the cleaned, filtered rental-bond dataset. |
| Deliverable 5 — join | `christchurch_airbnb_rental_joined.csv` — the merged Airbnb + rental-bond dataset used for all downstream analysis. |
| Deliverable 5 — analysis | `location_price_gap_summary.csv` and `airbnb_vs_long_term_rental_counts.csv` (the summary tables behind the two headline questions), plus the histogram, boxplot, and comparison bar chart figures. |

Every stage prints a running log of what it did to the console (row/column counts, invalid-value counts, missing-value counts, or — in Deliverable 5 — descriptive statistics and sample-size breakdowns), so the person running the pipeline can see what happened without needing to open every output file.

## 3. Main steps in the pipeline

### Deliverable 3 — combine and prepare
1. Load each of the nine monthly Airbnb listing files and filter each to Christchurch City listings only.
2. Add a `month_year` label to each month's data and concatenate all nine months into one combined dataset, processed through a single loop rather than handling any month (e.g. June 2026) as a special case.
3. Convert `price` to numeric and `last_review` to a proper date; add a fixed `scrape_date` and calculate `days_since_last_review` from it.
4. Only once all of the above processing is complete, save the combined dataset to `christchurch_listings_2025-10_to_2026-06.csv` — so the saved file reflects the final processed data, not an intermediate version.
5. Generate summary tables (missing values, numeric summary, categorical summary, category counts) and two exploratory visualisations (price distribution, days-since-last-review distribution), all saved to a dedicated `deliverable_3` output folder rather than the project root.

### Deliverable 4 — clean (`changed_airbnb_deliverable_4.py`)
1. Load the raw CSV with all columns read as strings, to avoid pandas guessing types before explicit validation.
2. Standardise whitespace and blank strings to a consistent missing-value marker.
3. Remove exact duplicate rows; verify no listing is missing an ID or month, and that no `(id, month_year)` pair is duplicated.
4. Verify the data covers only the expected month range and city — the script stops rather than silently processing unexpected data.
5. Validate every numeric column against column-specific rules (e.g. `price` and `minimum_nights` must be positive; coordinates must fall within valid bounds; `availability_365` must be between 0 and 365). Values that fail validation are set to missing, not guessed or dropped as whole rows.
6. Parse and validate review dates; flag (but retain) any review date that falls after the end of its labelled month.
7. Apply two explicit, documented judgement calls: missing prices are **retained** (not imputed), and unusually high prices are **retained** (not capped or removed), because an extreme value is not, by itself, evidence of an error.
8. Flag (but do not attempt to fix) host IDs that appear to have been stored in scientific notation.
9. Drop columns not needed for the analysis (`name`, `host_name`, and `license` if entirely empty).
10. Save the cleaned dataset, and generate a markdown report describing every decision made in steps 2–9.

### Deliverable 4 — clean (`changed_rental_bond.py`)
1. Load the raw quarterly tenancy bond CSV and convert `TimeFrame` to a proper date type.
2. Filter to the three quarters overlapping the Airbnb data window, then check the filtered data contains **exactly** the three expected quarters — raising an error if a quarter is missing or unexpected.
3. Keep only the columns needed for the downstream analysis; raise an error immediately if any expected column is missing from the source.
4. Drop rows missing an essential identifier; remove completely duplicated rows.
5. Convert `Number Of Beds` to a labelled string category (it contains non-numeric values like `"5+"` and `"ALL"`), with missing values explicitly labelled `"Unknown"`.
6. Convert numeric columns; validate negative values — `Location Id = -99` is a known, documented sentinel for "unknown/special location" and is deliberately preserved, while any other negative `Location Id` triggers an error.
7. Save the cleaned, filtered dataset to CSV.

### Deliverable 5 — join and analyse
Both scripts in this stage were refactored from an initial flat, top-to-bottom version into a set of clearly scoped functions called from a single `main()` entry point, with global constants (e.g. the minimum-observation reliability threshold) named at the top of the file rather than left as unlabelled literals mid-script.

1. **`join_datasets.py`** merges the cleaned Airbnb listings and the cleaned rental-bond data on location and time period, retaining all Airbnb observations (a left-style join), producing `christchurch_airbnb_rental_joined.csv`. The join step now includes explicit validation: checking that the rental-bond join key is unique before joining, and confirming afterward that the left join has not unexpectedly increased the number of Airbnb rows — a check that would catch an accidental many-to-many join early, before it silently inflated every downstream count and statistic.
2. **`christchurch_airbnb_rental_analysis.py`** loads the joined dataset and checks all required columns are present before proceeding, raising a clear error if any are missing rather than failing later with a less informative exception.
3. Removes duplicate listing-month observations that can arise from the join.
4. Converts the long-term weekly rent to a nightly equivalent (`Geometric Mean Rent / 7`) so it is directly comparable with the Airbnb nightly `price`.
5. Calculates `Price_Gap = price − Long_Term_Nightly_Rent` for every observation, and inspects the resulting distribution before drawing conclusions — this step surfaced a small number of extreme values (verified against Deliverable 4's own documented decision to retain, not cap, unusually high prices), which required the histogram to be built from an IQR-based, outlier-excluded view for readability, while the underlying data and summary statistics keep every observation.
6. Summarises the price gap by `Location Id` using the **median** (robust to outliers) rather than the mean as the headline statistic, and additionally restricts the "largest gap" comparison to locations with a minimum number of Airbnb observations, after discovering that the single largest raw median gap came from a location with only three listings — an unreliable sample size for a median comparison.
7. Produces a boxplot of the top locations by median price gap, built from the same reliability-filtered set of locations used in step 6, so the chart and the written conclusion are consistent with each other.
8. Separately, loads the rental-bond data again to compare **property counts**: filters to `Dwelling Type == "ALL"` and `Number Of Beds == "ALL"` for overall totals, and explicitly excludes the `Location Id = -99` placeholder code from this comparison (since it is a non-geographic sentinel, not a real suburb, and including it distorted the chart's scale by two orders of magnitude).
9. Counts unique Airbnb listings and total long-term rental bonds by location, merges the two counts, and calculates each location's Airbnb share of total properties.
10. Plots the comparison as a chart, capped to a readable number of locations (rather than attempting to show all ~90 locations with at least one Airbnb listing on a single chart, which produced illegible, overlapping axis labels).
11. Saves both summary tables to CSV for use in the final written report.

A related script, `Stats_area_api_query.py`, queries the Koordinates API to support the geographic-area lookup used elsewhere in Deliverable 5. Its API key was moved out of the script and into an environment variable, so the credential is no longer stored in the codebase itself.

## 4. Coding and software strategies adopted

- **Named constants instead of inline "magic values".** Deliverable 4's scripts group configuration (expected date ranges, expected columns, the `-99` sentinel, default filenames) into named constants near the top of the file. Deliverable 3 does the same with its parameter section (`price_plot_quantile`, `scrape_date`, etc.), replacing repeated hard-coded literals with descriptive names. This is a standard **DRY (Don't Repeat Yourself) / single-source-of-truth** practice: it makes the pipeline's assumptions visible and changeable in one place, and avoids the risk (explicitly noted in the peer's Deliverable 4 notes) of the same value being written in two places and drifting out of sync.

- **Fail-fast, defensive validation.** Rather than silently continuing when data doesn't match expectations, Deliverable 4's scripts raise an explicit error as soon as an assumption is violated (unexpected month/city, missing required column, duplicated listing-month pair, an unexpected negative `Location Id`, or a missing expected quarter). This is deliberate defensive programming: the pipeline stops and reports a problem rather than continuing on data that may already be wrong.

- **Missing and extreme data preserved, not guessed or silently removed.** Deliverable 4 sets invalid values to missing rather than inventing a replacement, and explicitly documents the decision to retain (not cap) unusually high prices. Deliverable 5 follows the same principle downstream: extreme price-gap values are kept in the underlying data and statistics, and only excluded from one specific visualisation (the histogram) for readability, with that exclusion stated explicitly rather than left implicit.

- **Statistical caution before drawing conclusions.** In Deliverable 5, a "top result" (the location with the single largest median price gap) was checked against its sample size before being reported as the headline answer, once a location with only three observations was found sitting at the top of the ranking. This reflects a broader coding/analysis discipline of sanity-checking pipeline output rather than accepting the first computed result — the same discipline applied to the property-count comparison, where a placeholder location code (`-99`) inflating the chart's scale by two orders of magnitude was investigated and traced to its source before being excluded, rather than assumed to be correct because "the code ran without errors."

- **Single-responsibility functions, with a clear entry point.** Deliverable 4's scripts centre on one function (`clean()`) with a clearly scoped job, supported by small helper functions (e.g. `log()` and `table()`) that each do one thing. Deliverable 5's two scripts were refactored the same way: the original flat, top-to-bottom analysis script was broken into individual functions (loading, cleaning, gap calculation, location summarising, plotting, property-count comparison), each callable and testable on its own, with a single `main()` function providing one clear entry point that calls them in order. This separates the pipeline's *structure* (the order steps run in) from its *logic* (what each step does) — a standard **separation of concerns** practice, and makes it possible to re-run or reuse one step (e.g. just the plotting function) without re-running the whole script.

- **Self-documenting output.** Deliverable 4's Airbnb script builds a structured log of every decision, reason, and consequence as it runs, and turns that log directly into the generated markdown report, so the documentation cannot drift out of sync with what the code actually did. Deliverable 5's analysis script follows the same spirit, and was further improved with clearer, more descriptive console output messages, so that a marker or teammate running the script can immediately see what happened at each step and spot problems without needing to read the code.

- **Reproducibility via command-line arguments and relative, project-root-based paths.** Deliverable 4's scripts accept optional input/output paths via `argparse`, with sensible defaults; Deliverable 3 resolves its input/output folders relative to the script's own location (`Path(__file__).parent`) rather than the working directory it happens to be run from. Deliverable 5's scripts were similarly updated to replace hard-coded absolute file paths (which only worked on the original author's machine) with relative paths anchored to the project root. This was a deliberate fix, since running the pipeline from different working directories, or on a different teammate's machine, had previously caused `FileNotFoundError`s during development — a problem worked through directly in this project before the fix was made.

- **Validating a join, not just trusting it.** `join_datasets.py` checks that its join key is unique on the rental-bond side, and confirms after joining that the number of Airbnb rows has not unexpectedly grown. An accidental many-to-many join is a common and easy-to-miss data wrangling mistake — it doesn't raise an error by itself, but silently duplicates rows and inflates every count and average calculated afterward. Checking for it immediately, right where the join happens, is far more reliable than trying to notice the effect later in a chart or summary statistic.

- **Keeping credentials out of the codebase.** The Koordinates API key used in `Stats_area_api_query.py` was moved from being hard-coded in the script to being read from an environment variable. This is a standard configuration/security practice: it means the key is never committed to version control or visible to anyone who can read the source file, and it can be changed or rotated without editing code.

---

## Appendix: Sanity check example

### `Location Id` = -99 handling (Deliverable 4 — `changed_rental_bond.py`)

**What `Location Id = -99` is, and why it needs checking.** The rental-bond dataset uses real numeric codes for `Location Id` (e.g. `322800`, `327000`) to identify specific Christchurch suburbs/areas. Some rows instead use `-99` — a **placeholder code**, not a real location, commonly used in government/statistical datasets to mean "unknown," "unclassified," or "not assigned to a specific area."

**The risk if this isn't handled correctly:**
1. The cleaning script could treat `-99` as just another negative number, and fail to distinguish it from a genuinely broken value (e.g. `-5` from a data-entry error) — meaning real data errors could slip through undetected.
2. Or the script could strip `-99` out entirely, assuming any negative value is invalid — losing rows that should be deliberately kept, with the placeholder treated as a valid category.

**What the script is supposed to do.** `changed_rental_bond.py` is written to do exactly one thing correctly: **keep** rows where `Location Id = -99` (a known, deliberate placeholder), and **reject/flag** rows where `Location Id` is any *other* negative number (which would be unexpected and likely a genuine data error).

**Step being checked:** the script's negative-value validation logic for `Location Id`.

**Why this matters in practice, not just in theory:** this is exactly the kind of issue that caused a real problem earlier in this project — `-99` appeared as an outsized bar in a Deliverable 5 property-count comparison chart, distorting the chart's scale by two orders of magnitude, before being investigated and explicitly excluded from that specific analysis (see Deliverable 5, step 8, above). This sanity check confirms the *cleaning* stage itself handles the value correctly, rather than relying on it being caught later by chance during analysis.

**How the check works, in plain terms:** load the cleaned dataset, find every row where `Location Id` is negative, and list the distinct negative values present. If the cleaning script is working correctly, this should show **only** `-99` — nothing else. If it showed something like `[-99, -5, -12]`, that would mean unexpected, invalid negative values slipped through the cleaning process without being caught.

**Verification run**, against the cleaned output (`rental_bond_cleaned_filtered.csv`):

```python
import pandas as pd
cleaned = pd.read_csv('rental_bond_cleaned_filtered.csv')
print(cleaned[cleaned['Location Id'] < 0]['Location Id'].unique())
```

**Output:**
```
[-99]
```

**Conclusion:** only `-99` appears — no other negative values exist in the cleaned dataset. This confirms the script's handling of this placeholder value works exactly as intended: the expected special case is preserved, and nothing unexpected or broken is hiding alongside it.

---

