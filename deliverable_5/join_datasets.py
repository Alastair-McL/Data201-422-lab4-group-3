"""Join Airbnb observations to quarterly rental-bond data by area and quarter."""

from pathlib import Path

import pandas as pd


AIRBNB_INPUT = Path("deliverable_5/christchurch_listings_cleaned_area_codes.csv")
BOND_INPUT = Path("deliverable_4/rental_bond_cleaned_filtered.csv")
OUTPUT_FILE = Path("deliverable_5/christchurch_airbnb_rental_joined.csv")

AIRBNB_REQUIRED_COLUMNS = {"month_year", "area_code"}
BOND_REQUIRED_COLUMNS = {
    "TimeFrame",
    "Location Id",
    "Dwelling Type",
    "Number Of Beds",
}


def validate_columns(df, required_columns, dataset_name):
    """Raise an error if a dataset is missing required columns."""

    missing_columns = required_columns.difference(df.columns)
    if missing_columns:
        raise ValueError(
            f"{dataset_name} is missing required columns: "
            f"{sorted(missing_columns)}"
        )


def prepare_airbnb_data(path):
    """Load Airbnb data and create the quarter key used by the bond data."""

    airbnb = pd.read_csv(path)
    validate_columns(airbnb, AIRBNB_REQUIRED_COLUMNS, "Airbnb dataset")

    airbnb["TimeFrame"] = (
        pd.to_datetime(airbnb["month_year"], errors="raise")
        .dt.to_period("Q")
        .dt.start_time
        .dt.strftime("%Y-%m-%d")
    )
    airbnb["area_code"] = pd.to_numeric(
        airbnb["area_code"], errors="coerce"
    ).astype("Int64")

    return airbnb


def prepare_bond_data(path):
    """Load the overall quarterly rental-bond rows."""

    bonds = pd.read_csv(path)
    validate_columns(bonds, BOND_REQUIRED_COLUMNS, "Rental-bond dataset")

    bonds_all = bonds[
        (bonds["Dwelling Type"] == "ALL")
        & (bonds["Number Of Beds"] == "ALL")
    ].copy()

    bonds_all["Location Id"] = pd.to_numeric(
        bonds_all["Location Id"], errors="coerce"
    ).astype("Int64")

    duplicate_keys = bonds_all.duplicated(
        ["Location Id", "TimeFrame"]
    ).sum()

    if duplicate_keys:
        raise ValueError(
            "Rental-bond join key is not unique: "
            f"{duplicate_keys} duplicate Location Id/TimeFrame rows found."
        )

    return bonds_all


def main():
    """Create and validate the Airbnb/rental-bond left join."""

    airbnb = prepare_airbnb_data(AIRBNB_INPUT)
    bonds_all = prepare_bond_data(BOND_INPUT)

    merged = pd.merge(
        airbnb,
        bonds_all,
        left_on=["area_code", "TimeFrame"],
        right_on=["Location Id", "TimeFrame"],
        how="left",
        validate="many_to_one",
    )

    if len(merged) != len(airbnb):
        raise ValueError(
            "Left join changed the number of Airbnb rows: "
            f"{len(airbnb)} input rows -> {len(merged)} joined rows."
        )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(OUTPUT_FILE, index=False)

    matched_rows = merged["Location Id"].notna().sum()

    print(f"Airbnb rows: {len(airbnb)}")
    print(f"Joined rows: {len(merged)}")
    print(f"Rows with matching bond data: {matched_rows}")
    print(f"Rows without matching bond data: {len(merged) - matched_rows}")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
