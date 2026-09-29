"""Calculate the median Airbnb price for Christchurch Central."""

from pathlib import Path

import pandas as pd


INPUT_FILE = Path("deliverable_5/christchurch_airbnb_rental_joined.csv")
CHRISTCHURCH_CENTRAL_ID = 326600
REQUIRED_COLUMNS = {"Location Id", "id", "month_year", "price"}


def main():
    """Calculate and print the median nightly Airbnb price."""

    df = pd.read_csv(INPUT_FILE)

    missing_columns = REQUIRED_COLUMNS.difference(df.columns)
    if missing_columns:
        raise ValueError(
            f"Input file is missing required columns: {sorted(missing_columns)}"
        )

    central = df[
        df["Location Id"] == CHRISTCHURCH_CENTRAL_ID
    ].drop_duplicates(
        subset=["id", "month_year"]
    )

    if central.empty:
        raise ValueError(
            f"No Airbnb observations found for Location Id "
            f"{CHRISTCHURCH_CENTRAL_ID}."
        )

    median_price = central["price"].median()

    if pd.isna(median_price):
        raise ValueError("No valid Airbnb prices were found for Christchurch Central.")

    print(
        "Median Airbnb price in Christchurch Central: "
        f"${median_price:.2f}"
    )


if __name__ == "__main__":
    main()
