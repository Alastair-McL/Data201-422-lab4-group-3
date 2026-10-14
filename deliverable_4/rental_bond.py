"""
Deliverable 4: clean the rental bond dataset and filter it to the
October 2025 - June 2026 period used for the Airbnb comparison.

Reads the quarterly tenancy bond CSV, keeps the columns needed for
rental-price, property-count, dwelling-type and bedroom-category
analysis, validates identifiers and numeric ranges, and writes the
cleaned, filtered dataset to a new CSV.
"""
import argparse
from pathlib import Path
import pandas as pd

# ---------------------------------------------------------------------------
# Parameters (grouped here, instead of scattered through the script, so the
# behaviour of the script can be checked/changed in one place)
# ---------------------------------------------------------------------------
DEFAULT_INPUT_FILENAME = "Detailed-Quarterly-Tenancy-Q1-2020-Q3-2026.csv"
DEFAULT_OUTPUT_FILENAME = "rental_bond_cleaned_filtered.csv"

START_DATE = pd.Timestamp("2025-10-01")
END_DATE = pd.Timestamp("2026-06-30")
# The quarterly data is expected to contain exactly these three quarter
# start-dates once filtered to START_DATE..END_DATE. Checked explicitly
# below, rather than only described in this comment, so a source change
# (a missing or unexpected quarter) is caught rather than silently passed
# through the pipeline.
EXPECTED_QUARTERS = [
    pd.Timestamp("2025-10-01"),
    pd.Timestamp("2026-01-01"),
    pd.Timestamp("2026-04-01"),
]

# Location Id -99 is a known code meaning "unknown/special location" in this
# dataset (per the source documentation) and is deliberately preserved, not
# treated as an invalid negative value below.
KNOWN_SPECIAL_LOCATION_ID = -99

COLUMNS_TO_KEEP = [
    "TimeFrame",
    "Location Id",
    "Dwelling Type",
    "Number Of Beds",
    "Total Bonds",
    "Active Bonds",
    "Closed Bonds",
    "Median Rent",
    "Geometric Mean Rent",
    "Upper Quartile Rent",
    "Lower Quartile Rent",
    "Log Std Dev Weekly Rent",
]

NUMERIC_COLUMNS = [
    "Location Id",
    "Total Bonds",
    "Active Bonds",
    "Closed Bonds",
    "Median Rent",
    "Geometric Mean Rent",
    "Upper Quartile Rent",
    "Lower Quartile Rent",
    "Log Std Dev Weekly Rent",
]

NON_NEGATIVE_COLUMNS = [
    "Total Bonds",
    "Active Bonds",
    "Closed Bonds",
    "Median Rent",
    "Geometric Mean Rent",
    "Upper Quartile Rent",
    "Lower Quartile Rent",
    "Log Std Dev Weekly Rent",
]


def clean(source, output_file):
    source, output_file = Path(source), Path(output_file)

    # ---------------------------------------------------------------
    # 1. Load the rental bond dataset
    # ---------------------------------------------------------------
    bond_data = pd.read_csv(source)
    print("Rental bond dataset loaded successfully.")
    print("Original dataset shape:", bond_data.shape)
    print("\nOriginal dataset columns:")
    print(bond_data.columns.tolist())
    print("\nOriginal timeframe values:")
    print(bond_data["TimeFrame"].unique())

    # ---------------------------------------------------------------
    # 2. Convert TimeFrame to datetime
    # ---------------------------------------------------------------
    bond_data["TimeFrame"] = pd.to_datetime(bond_data["TimeFrame"], errors="coerce")
    invalid_timeframes = bond_data["TimeFrame"].isna().sum()
    print("\nInvalid timeframe values:", invalid_timeframes)

    # ---------------------------------------------------------------
    # 3. Filter the quarters from October 2025 to June 2026, then check
    #    the filtered data actually contains the expected quarters.
    # ---------------------------------------------------------------
    filtered_bond_data = bond_data[
        (bond_data["TimeFrame"] >= START_DATE) & (bond_data["TimeFrame"] <= END_DATE)
    ].copy()

    observed_quarters = sorted(filtered_bond_data["TimeFrame"].dropna().unique())
    if list(observed_quarters) != EXPECTED_QUARTERS:
        raise ValueError(
            "Filtered data does not contain exactly the expected quarters "
            f"{[d.date() for d in EXPECTED_QUARTERS]}; found "
            f"{[pd.Timestamp(d).date() for d in observed_quarters]}. Inspect the source file."
        )

    print("\nNumber of rows for each timeframe:")
    print(filtered_bond_data["TimeFrame"].value_counts().sort_index())
    print("\nFiltered rental bond dataset shape:", filtered_bond_data.shape)
    print("\nMissing values before cleaning:")
    print(filtered_bond_data.isnull().sum())

    # ---------------------------------------------------------------
    # 4. Select relevant columns
    # ---------------------------------------------------------------
    # These columns are retained for rental-price, property-count,
    # dwelling-type, and bedroom-category analysis. Location Id and
    # TimeFrame are retained for identifying and comparing records over
    # time. Dwelling Type is retained because it may distinguish
    # different types of rental properties.
    missing_columns = [c for c in COLUMNS_TO_KEEP if c not in filtered_bond_data.columns]
    if missing_columns:
        raise KeyError(f"The following columns are missing from the dataset: {missing_columns}")
    filtered_bond_data = filtered_bond_data[COLUMNS_TO_KEEP].copy()
    print("\nColumns retained for analysis:")
    print(filtered_bond_data.columns.tolist())

    # ---------------------------------------------------------------
    # 5. Remove rows with missing essential identifiers
    # ---------------------------------------------------------------
    rows_before = len(filtered_bond_data)
    filtered_bond_data = filtered_bond_data.dropna(subset=["Location Id", "TimeFrame"])
    print("\nRows removed because of missing identifiers:", rows_before - len(filtered_bond_data))
    print("Shape after removing missing identifiers:", filtered_bond_data.shape)

    # ---------------------------------------------------------------
    # 6. Check and remove completely duplicated rows
    # ---------------------------------------------------------------
    duplicate_count = filtered_bond_data.duplicated().sum()
    print("\nCompletely duplicated rows found:", duplicate_count)
    filtered_bond_data = filtered_bond_data.drop_duplicates()
    print("Shape after removing duplicate rows:", filtered_bond_data.shape)

    # ---------------------------------------------------------------
    # 7. Convert numeric columns and handle Number Of Beds
    # ---------------------------------------------------------------
    # Number Of Beds is kept as a categorical/string column: it contains
    # values such as '5+' and 'ALL', which are not exact numeric values.
    # Missing bed-category values are labelled 'Unknown' because missing
    # information does not mean zero beds.
    filtered_bond_data["Number Of Beds"] = (
        filtered_bond_data["Number Of Beds"].astype("string").fillna("Unknown")
    )
    print("\nNumber Of Beds values:")
    print(filtered_bond_data["Number Of Beds"].value_counts(dropna=False).sort_index())

    for column in NUMERIC_COLUMNS:
        filtered_bond_data[column] = pd.to_numeric(filtered_bond_data[column], errors="coerce")
    filtered_bond_data["Location Id"] = filtered_bond_data["Location Id"].astype("Int64")

    # ---------------------------------------------------------------
    # 8. Check for invalid negative values
    # ---------------------------------------------------------------
    # Negative values are not expected for the measurement columns below.
    # Location Id is an identifier: the only negative value expected is
    # the known special code, checked explicitly rather than only in a
    # comment, so an unexpected negative Location Id is caught here
    # instead of silently passing through the pipeline.
    other_negative_location_ids = filtered_bond_data.loc[
        (filtered_bond_data["Location Id"] < 0)
        & (filtered_bond_data["Location Id"] != KNOWN_SPECIAL_LOCATION_ID),
        "Location Id",
    ].unique()
    if len(other_negative_location_ids) > 0:
        raise ValueError(
            "Unexpected negative Location Id values found (not the known "
            f"special code {KNOWN_SPECIAL_LOCATION_ID}): {sorted(other_negative_location_ids)}"
        )

    for column in NON_NEGATIVE_COLUMNS:
        negative_count = (filtered_bond_data[column] < 0).sum()
        print(f"Negative values in {column}:", negative_count)
        filtered_bond_data.loc[filtered_bond_data[column] < 0, column] = pd.NA

    # ---------------------------------------------------------------
    # 9. Check and save the cleaned dataset
    # ---------------------------------------------------------------
    print("\nMissing values after cleaning:")
    print(filtered_bond_data.isnull().sum())
    print("\nFinal cleaned dataset shape:", filtered_bond_data.shape)
    print("\nFinal cleaned dataset preview:")
    print(filtered_bond_data.head())

    filtered_bond_data.to_csv(output_file, index=False)
    print("\nCleaned and filtered dataset saved successfully as:", output_file)
    return filtered_bond_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", default=None)
    parser.add_argument("--output-file", default=None)
    args = parser.parse_args()

    script_folder = Path(__file__).parent

    input_file = Path(args.input) if args.input else script_folder / DEFAULT_INPUT_FILENAME
    output_path = (
        Path(args.output_file) if args.output_file else script_folder / DEFAULT_OUTPUT_FILENAME
    )

    clean(input_file, output_path)