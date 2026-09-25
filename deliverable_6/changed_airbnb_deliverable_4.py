"""
DATA 201 Deliverable 4  points 1–2: clean listings and report decisions.

Clean the Christchurch Airbnb listings dataset and report cleaning decisions.
Save the cleaned dataset and a markdown report of the cleaning decisions.
Copy this file to a new folder that contains the combined Christchurch CSV file, then run it from that folder.
"""
import argparse
from pathlib import Path
import pandas as pd

# ---------------------------------------------------------------------------
# Parameters (kept together and named, rather than as literals inline below)
# ---------------------------------------------------------------------------
EXPECTED_MONTH_START = "2025-10"
EXPECTED_MONTH_END = "2026-06"
EXPECTED_CITY = "Christchurch City"
DEFAULT_INPUT_FILENAME = "christchurch_listings_2025-10_to_2026-06.csv"
DEFAULT_OUTPUT_DIRNAME = "cleaned"
OUTPUT_CSV_NAME = "christchurch_listings_cleaned.csv"
OUTPUT_REPORT_NAME = "deliverable_4_cleaning_notes.md"


def clean(source, output_dir):
    source, output_dir = Path(source), Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / OUTPUT_CSV_NAME
    if source.resolve() == target.resolve():
        raise ValueError("Choose an output directory that does not overwrite the input.")
    raw = pd.read_csv(source, dtype="string")
    df = raw.copy()
    decisions = []

    def log(decision, reason, consequence):
        decisions.append((decision, reason, consequence))

    # Standardise surrounding whitespace and empty strings only.
    whitespace = sum(int((df[column].notna() & df[column].ne(df[column].str.strip())).sum()) for column in df)
    for column in df:
        df[column] = df[column].str.strip().replace("", pd.NA)
    log("Trim text and standardise blanks", "Whitespace can create inconsistent categories.",
        f"{whitespace:,} cells had surrounding whitespace; no rows removed.")

    # The same listing can legitimately appear in several monthly snapshots.
    duplicates = int(df.duplicated().sum())
    df = df.drop_duplicates().copy()
    if df[["id", "month_year"]].isna().any().any():
        raise ValueError("Missing listing ID or month: inspect source before proceeding.")
    if df.duplicated(["id", "month_year"]).any():
        raise ValueError("Conflicting listing-month records require manual inspection.")
    if not df.id.str.fullmatch(r"\d+").all():
        raise ValueError("Unexpected listing ID format.")
    log("Check duplicates using listing ID and month", "Repeated IDs in different months describe different observations.",
        f"{duplicates:,} exact duplicate rows removed; no conflicting listing-month pairs.")

    expected = pd.period_range(EXPECTED_MONTH_START, EXPECTED_MONTH_END, freq="M").astype(str)
    if not df.month_year.isin(expected).all() or not df.neighbourhood_group.eq(EXPECTED_CITY).all():
        raise ValueError("Unexpected month or city: inspect the input.")

    # Validate numbers. Preserve missing values instead of guessing replacements.
    integer_columns = ["minimum_nights", "number_of_reviews", "calculated_host_listings_count",
                       "availability_365", "number_of_reviews_ltm"]
    numeric_columns = ["latitude", "longitude", "price", "reviews_per_month"] + integer_columns
    for column in numeric_columns:
        original = df[column]
        cleaned = original.str.replace("$", "", regex=False).str.replace(",", "", regex=False) if column == "price" else original
        values = pd.to_numeric(cleaned, errors="coerce").astype("Float64")
        bad = values.isin([float("inf"), -float("inf")])
        if column in integer_columns:
            bad |= values.mod(1).ne(0)
        if column in ["price", "minimum_nights", "calculated_host_listings_count"]:
            bad |= values.le(0)
        elif column not in ["latitude", "longitude"]:
            bad |= values.lt(0)
        if column == "availability_365":
            bad |= values.gt(365)
        if column == "latitude":
            bad |= ~values.between(-90, 90)
        if column == "longitude":
            bad |= ~values.between(-180, 180)
        values = values.mask(bad.fillna(False))
        invalid = int((original.notna() & values.isna()).sum())
        df[column] = values.astype("Int64") if column in integer_columns else values
        log(f"Validate {column}", "Use numeric values and reject impossible ranges; retain unknown values as missing.",
            f"{invalid:,} invalid values set to missing; {int(df[column].isna().sum()):,} missing after numeric validation, before later filling; no rows removed.")

    dates = pd.to_datetime(df.last_review, format="%Y-%m-%d", errors="coerce")
    invalid_dates = int((df.last_review.notna() & dates.isna()).sum())
    late = dates.gt(pd.to_datetime(df.month_year) + pd.offsets.MonthEnd(0))
    df["last_review"] = dates.dt.strftime("%Y-%m-%d").astype("string")
    df["review_after_month_end"] = late
    no_reviews = df.number_of_reviews.eq(0) & df.reviews_per_month.isna()
    df.loc[no_reviews, "reviews_per_month"] = 0
    log("Keep missing review dates; fill review rate only for zero-review listings",
        "A listing with no reviews has no last review date. Zero reviews supports a zero observed review rate.",
        f"{int(no_reviews.sum()):,} review rates filled with 0; {int(df.last_review.isna().sum()):,} dates remain missing; {invalid_dates:,} invalid dates converted to missing; no rows removed.")
    log("Flag review dates after the labelled month", "Actual scrape dates are unavailable; do not guess corrected months or dates.",
        f"{int(late.sum()):,} records flagged in review_after_month_end and retained for source verification.")

    log("Retain missing prices and minimum nights", "Rows are still useful for listing counts; filling prices would invent rental information.",
        f"{int(df.price.isna().sum()):,} missing prices and {int(df.minimum_nights.isna().sum()):,} missing minimum_nights retained. Price summaries must exclude missing prices and report coverage.")
    log("Retain high positive prices", "An unusually high price is not proof of an error. No arbitrary percentile deletion or capping.",
        f"Maximum price {df.price.max():,.0f} NZD/night retained; no rows removed. Inspect extremes before using means.")
    scientific_hosts = int(df.host_id.str.contains("e", case=False, na=False).sum())
    log("Keep IDs as text, preserving host_id exactly", "Large identifiers can lose precision when converted to floating point.",
        f"{scientific_hosts:,} host_id values already use scientific notation in the source. Their original digits cannot be recovered here; do not use them for verified host joins without source checks.")
    drop = ["name", "host_name"]
    if "license" in df and df.license.isna().all():
        drop.append("license")
    df = df.drop(columns=drop)
    log("Drop " + ", ".join(drop), "Listing/host names are unnecessary for price and count comparisons; the license column is entirely empty when dropped.",
        f"{len(drop)} columns removed; no rows removed. IDs, month, city, neighbourhood, room type, coordinates, availability and review measures retained.")

    # Keep original row order and coordinate precision. CSV has no persistent dtype metadata.
    df.to_csv(target, index=False, lineterminator="\n")
    monthly = df.groupby("month_year").agg(records=("id", "size"), unique_listings=("id", "nunique"),
                                          usable_prices=("price", "count"))
    monthly["missing_prices"] = monthly.records - monthly.usable_prices
    monthly["price_coverage_percent"] = (100 * monthly.usable_prices / monthly.records).round(2)
    missing = pd.DataFrame({"missing_before": raw.isna().sum(), "missing_after": df.isna().sum()})
    missing["status"] = ["dropped" if column not in df else "added" if column not in raw else "retained" for column in missing.index]

    def table(frame):
        return frame.fillna("—").to_string(index=False)

    report = f"""# Deliverable 4: Christchurch listings cleaning (points 1 and 2)

## Input and results

Input: `{source.name}`, created by Deliverable 3. The supplied README identifies Inside Airbnb as the source, with prices in NZD per night. This run uses the supplied CSV, without downloading replacement data.

- Before: {len(raw):,} listing-month records, {len(raw.columns)} columns.
- After: {len(df):,} listing-month records, {len(df.columns)} columns.
- Rows lost: {len(raw)-len(df):,}.
- Distinct listing IDs across all months: {df.id.nunique():,}.
- pandas version used: {pd.__version__}.

A row describes one listing in one labelled month. Count unique IDs within each month; summing monthly counts counts repeated observations, not unique properties across the whole period.

## Decisions, reasons and consequences

{table(pd.DataFrame(decisions, columns=["Decision", "Reason", "Consequence"]))}

## Price coverage by month

{table(monthly.reset_index())}

December 2025, January 2026 and February 2026 contain no prices in the supplied file. Their average or median price is unavailable, not zero. Keeping these records preserves listing counts. Recovering these prices would require checking the original source files. Missing prices can bias comparisons if listings with prices differ from those without prices.

## Missing values before and after

{table(missing.rename_axis("column").reset_index())}

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

When reloading the output in pandas, use `dtype={{"id": "string", "host_id": "string"}}` to preserve identifiers. `month_year` is YYYY-MM text; `last_review` is YYYY-MM-DD text with blank values for missing dates. Numeric missing values are exported as blank cells.
"""
    (output_dir / OUTPUT_REPORT_NAME).write_text(report, encoding="utf-8")
    print(f"Cleaned {len(raw):,} -> {len(df):,} rows; {len(raw.columns)} -> {len(df.columns)} columns.")
    print(monthly.to_string())
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", default=None)
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    script_folder = Path(__file__).parent

    input_file = (
        Path(args.input)
        if args.input
        else script_folder / DEFAULT_INPUT_FILENAME
    )

    output_folder = (
        Path(args.output_dir)
        if args.output_dir
        else script_folder / DEFAULT_OUTPUT_DIRNAME
    )

    clean(input_file, output_folder)