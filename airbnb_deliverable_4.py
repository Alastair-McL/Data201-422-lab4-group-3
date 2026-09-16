"""
DATA 201 Deliverable 4
Clean the Christchurch Airbnb listings dataset and report cleaning decisions.
Save the cleaned dataset and a markdown report of the cleaning decisions.
Copy this file to a new folder that contains the combined Christchurch CSV file, then run it from that folder.
Run:
    python airbnb_deliverable_4.py

Or:
    python airbnb_deliverable_4.py input.csv --output-dir cleaned

The original CSV is never overwritten.
"""

import argparse
from pathlib import Path
import pandas as pd


EXPECTED_MONTHS = pd.period_range(
    "2025-10", "2026-06", freq="M"
).astype(str)

INTEGER_COLUMNS = [
    "minimum_nights",
    "number_of_reviews",
    "calculated_host_listings_count",
    "availability_365",
    "number_of_reviews_ltm",
]

NUMERIC_COLUMNS = [
    "latitude",
    "longitude",
    "price",
    "reviews_per_month",
] + INTEGER_COLUMNS


def clean(source, output_dir):
    source = Path(source)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    target = output_dir / "christchurch_listings_cleaned.csv"
    notes_file = output_dir / "deliverable_4_cleaning_notes.md"

    if source.resolve() == target.resolve():
        raise ValueError(
            "The output file cannot overwrite the input file."
        )

    # --------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------

    raw = pd.read_csv(source, dtype="string")
    df = raw.copy()

    decisions = []

    def log(decision, reason, consequence):
        decisions.append(
            {
                "Decision": decision,
                "Reason": reason,
                "Consequence": consequence,
            }
        )

    print(f"Loaded {len(df):,} rows and {len(df.columns):,} columns.")


    # --------------------------------------------------
    # TEXT CLEANING
    # --------------------------------------------------

    whitespace_cells = 0

    for column in df.columns:
        whitespace_cells += int(
            (
                df[column].notna()
                & df[column].ne(df[column].str.strip())
            ).sum()
        )

        df[column] = (
            df[column]
            .str.strip()
            .replace("", pd.NA)
        )

    log(
        "Trim whitespace and standardise blanks",
        "Whitespace can create inconsistent categories.",
        f"{whitespace_cells:,} cells were trimmed; no rows removed.",
    )


    # --------------------------------------------------
    # DUPLICATES
    # --------------------------------------------------

    exact_duplicates = int(df.duplicated().sum())
    df = df.drop_duplicates().copy()

    # These columns are required for identifying a listing-month record.
    required = ["id", "month_year", "neighbourhood_group"]

    missing_required = [
        column for column in required
        if column not in df.columns
    ]

    if missing_required:
        raise ValueError(
            f"Required columns are missing: {missing_required}"
        )

    if df[["id", "month_year"]].isna().any().any():
        raise ValueError(
            "Some records have a missing ID or month_year. "
            "Inspect the source before continuing."
        )

    if df.duplicated(["id", "month_year"]).any():
        raise ValueError(
            "Conflicting listing-month records were found. "
            "Manual inspection is required."
        )

    log(
        "Remove exact duplicate rows",
        "Exact duplicates provide no additional information.",
        f"{exact_duplicates:,} exact duplicate rows removed.",
    )


    # --------------------------------------------------
    # CHECK MONTH AND CITY
    # --------------------------------------------------

    unexpected_months = (
        df.loc[
            ~df["month_year"].isin(EXPECTED_MONTHS),
            "month_year"
        ]
        .dropna()
        .unique()
        .tolist()
    )

    if unexpected_months:
        raise ValueError(
            f"Unexpected month_year values found: {unexpected_months}"
        )

    unexpected_city = (
        ~df["neighbourhood_group"].eq("Christchurch City")
    ).sum()

    if unexpected_city:
        raise ValueError(
            f"{unexpected_city:,} records are not labelled "
            "'Christchurch City'."
        )


    # --------------------------------------------------
    # VALIDATE NUMERIC VARIABLES
    # --------------------------------------------------

    for column in NUMERIC_COLUMNS:

        if column not in df.columns:
            continue

        original = df[column]

        if column == "price":
            cleaned = (
                original
                .str.replace("$", "", regex=False)
                .str.replace(",", "", regex=False)
            )
        else:
            cleaned = original

        values = pd.to_numeric(
            cleaned,
            errors="coerce"
        ).astype("Float64")

        invalid = values.isin(
            [float("inf"), -float("inf")]
        )

        # Integer columns must contain whole numbers.
        if column in INTEGER_COLUMNS:
            invalid |= values.mod(1).ne(0)

        # These variables must be positive.
        if column in [
            "price",
            "minimum_nights",
            "calculated_host_listings_count",
        ]:
            invalid |= values.le(0)

        # Review counts/rates and availability cannot be negative.
        elif column not in ["latitude", "longitude"]:
            invalid |= values.lt(0)

        # Availability is measured over 365 days.
        if column == "availability_365":
            invalid |= values.gt(365)

        # Valid coordinate ranges.
        if column == "latitude":
            invalid |= ~values.between(-90, 90)

        if column == "longitude":
            invalid |= ~values.between(-180, 180)

        values = values.mask(
            invalid.fillna(False)
        )

        invalid_count = int(
            original.notna()
            .sum()
            - values.notna().sum()
        )

        if column in INTEGER_COLUMNS:
            df[column] = values.astype("Int64")
        else:
            df[column] = values

        log(
            f"Validate {column}",
            "Convert to numeric values and reject impossible values.",
            f"{invalid_count:,} invalid values set to missing; "
            f"no rows removed.",
        )


    # --------------------------------------------------
    # REVIEW DATES
    # --------------------------------------------------

    if "last_review" in df.columns:

        dates = pd.to_datetime(
            df["last_review"],
            format="%Y-%m-%d",
            errors="coerce",
        )

        invalid_dates = int(
            (
                df["last_review"].notna()
                & dates.isna()
            ).sum()
        )

        month_end = (
            pd.PeriodIndex(
                df["month_year"],
                freq="M"
            ).to_timestamp("M")
        )

        after_month_end = dates > month_end

        df["last_review"] = (
            dates.dt.strftime("%Y-%m-%d")
            .astype("string")
        )

        df["review_after_month_end"] = (
            after_month_end.fillna(False)
        )

        if (
            "number_of_reviews" in df.columns
            and "reviews_per_month" in df.columns
        ):
            no_reviews = (
                df["number_of_reviews"].eq(0)
                & df["reviews_per_month"].isna()
            )

            df.loc[
                no_reviews,
                "reviews_per_month"
            ] = 0

            filled_rates = int(no_reviews.sum())
        else:
            filled_rates = 0

        log(
            "Clean review dates and fill zero-review rates",
            "Listings with zero reviews have no previous review date. "
            "A zero observed review rate is reasonable for listings "
            "with zero reviews.",
            f"{filled_rates:,} review rates filled with 0; "
            f"{invalid_dates:,} invalid dates converted to missing.",
        )

        log(
            "Flag review dates after the labelled month",
            "The actual scrape date is unavailable, so dates are flagged "
            "rather than guessed or changed.",
            f"{int(after_month_end.sum()):,} records flagged.",
        )


    # --------------------------------------------------
    # PRICE AND MISSING VALUES
    # --------------------------------------------------

    if "price" in df.columns:
        log(
            "Keep missing prices",
            "Missing prices should not be replaced with guessed values.",
            f"{int(df['price'].isna().sum()):,} missing prices retained.",
        )

        if df["price"].notna().any():
            log(
                "Keep high prices",
                "A high price is not automatically an error.",
                f"Maximum price retained: "
                f"{df['price'].max():,.0f} NZD/night.",
            )


    # --------------------------------------------------
    # REMOVE UNNECESSARY COLUMNS
    # --------------------------------------------------

    columns_to_drop = [
        column
        for column in ["name", "host_name"]
        if column in df.columns
    ]

    # Drop license only if it contains no information.
    if (
        "license" in df.columns
        and df["license"].isna().all()
    ):
        columns_to_drop.append("license")

    if columns_to_drop:
        df = df.drop(columns=columns_to_drop)

        log(
            "Drop " + ", ".join(columns_to_drop),
            "These fields are not required for the Deliverable 4 "
            "cleaning and comparison tasks.",
            f"{len(columns_to_drop)} columns removed; no rows removed.",
        )


    # --------------------------------------------------
    # SAVE CLEANED DATA
    # --------------------------------------------------

    df.to_csv(
        target,
        index=False,
        lineterminator="\n",
    )


    # --------------------------------------------------
    # SUMMARY TABLES
    # --------------------------------------------------

    monthly = (
        df.groupby("month_year")
        .agg(
            records=("id", "size"),
            unique_listings=("id", "nunique"),
            usable_prices=("price", "count"),
        )
        .reindex(EXPECTED_MONTHS)
    )

    monthly["missing_prices"] = (
        monthly["records"]
        - monthly["usable_prices"]
    )

    monthly["price_coverage_percent"] = (
        100
        * monthly["usable_prices"]
        / monthly["records"]
    ).round(2)

    missing = pd.DataFrame({
        "missing_before": raw.isna().sum(),
        "missing_after": df.isna().reindex(raw.index).sum(),
    })

    missing["status"] = missing.index.map(
        lambda column:
            "dropped"
            if column not in df.columns
            else "retained"
    )


    # --------------------------------------------------
    # REPORT
    # --------------------------------------------------

    decisions_table = pd.DataFrame(decisions)

    report = f"""# Deliverable 4: Christchurch listings cleaning

## Input and results

Input file: `{source.name}`

- Before: {len(raw):,} listing-month records
- After: {len(df):,} listing-month records
- Rows removed: {len(raw) - len(df):,}
- Columns before: {len(raw.columns)}
- Columns after: {len(df.columns)}
- Distinct listing IDs: {df["id"].nunique():,}
- pandas version: `{pd.__version__}`

A row represents one listing in one labelled month. The same listing can therefore appear in several monthly observations.

## Cleaning decisions

| Decision | Reason | Consequence |
| --- | --- | --- |
{chr(10).join(
    "| " + " | ".join(
        str(row[column]).replace("|", "\\|")
        for column in ["Decision", "Reason", "Consequence"]
    ) + " |"
    for _, row in decisions_table.iterrows()
)}

## Price coverage by month

{monthly.reset_index().to_string(index=False)}

December 2025, January 2026 and February 2026 contain no prices in the supplied file. Their price statistics are therefore unavailable rather than zero.

## Missing values

{missing.rename_axis("column").reset_index().to_string(index=False)}

## Important limitations

- Latitude and longitude were checked using their valid global coordinate ranges.
- The supplied Christchurch City label was retained rather than creating a new geographic boundary.
- Zero availability was retained. It does not establish whether a property is booked or blocked.
- `review_after_month_end` flags review dates that occur after the labelled month. These should be checked against the original source if necessary.
- Missing prices were retained rather than guessed or filled.
- High prices were retained rather than removed using an arbitrary percentile.
- Listing IDs were read as text to avoid numerical rounding.
"""

    notes_file.write_text(
        report,
        encoding="utf-8"
    )

    # --------------------------------------------------
    # FINISH
    # --------------------------------------------------

    print()
    print(
        f"Cleaned {len(raw):,} -> {len(df):,} rows."
    )
    print(
        f"Columns: {len(raw.columns)} -> {len(df.columns)}."
    )
    print(f"Saved: {target}")
    print(f"Report: {notes_file}")

    return df


# --------------------------------------------------
# RUN SCRIPT
# --------------------------------------------------

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description=__doc__
    )

    parser.add_argument(
        "input",
        nargs="?",
        default=None,
        help="Input combined Christchurch CSV.",
    )

    parser.add_argument(
        "--output-dir",
        default=None,
        help="Folder for cleaned data and report.",
    )

    args = parser.parse_args()

    # Always use the folder containing this script unless
    # the user supplies another path.
    script_folder = Path(__file__).parent

    input_file = (
        Path(args.input)
        if args.input
        else script_folder / "christchurch_listings_2025-10_to_2026-06.csv"
    )

    output_folder = (
        Path(args.output_dir)
        if args.output_dir
        else script_folder / "cleaned"
    )

    clean(input_file, output_folder)
