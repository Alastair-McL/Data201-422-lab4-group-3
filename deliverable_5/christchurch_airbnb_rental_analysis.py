"""Analyse Christchurch Airbnb prices against long-term rental prices.

The script answers two questions:
1. Where is the largest typical Airbnb/long-term rental price gap?
2. How do Airbnb listing counts compare with long-term rental bond counts?

Run from the project root so the relative paths below resolve correctly.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


JOINED_INPUT = Path("deliverable_5/christchurch_airbnb_rental_joined.csv")
BOND_INPUT = Path("deliverable_4/rental_bond_cleaned_filtered.csv")
GAP_OUTPUT = Path("deliverable_5/location_price_gap_summary.csv")
COUNT_OUTPUT = Path("deliverable_5/airbnb_vs_long_term_rental_counts.csv")

MIN_OBSERVATIONS = 20
OUTLIER_IQR_MULTIPLIER = 3
HISTOGRAM_BINS = 50
TOP_LOCATIONS_TO_PLOT = 15
TOP_COUNT_LOCATIONS_TO_PLOT = 20
RENTAL_COUNT_COLUMN = "Total Bonds"

REQUIRED_JOINED_COLUMNS = {
    "id",
    "month_year",
    "price",
    "Location Id",
    "Geometric Mean Rent",
}
REQUIRED_BOND_COLUMNS = {
    "Location Id",
    "Dwelling Type",
    "Number Of Beds",
    RENTAL_COUNT_COLUMN,
}


def validate_columns(df, required_columns, dataset_name):
    """Raise an error if a dataset is missing required columns."""

    missing_columns = required_columns.difference(df.columns)
    if missing_columns:
        raise ValueError(
            f"{dataset_name} is missing required columns: "
            f"{sorted(missing_columns)}"
        )


def load_joined_data(path):
    """Load the joined data and remove duplicate listing-month observations."""

    df = pd.read_csv(path)
    validate_columns(df, REQUIRED_JOINED_COLUMNS, "Joined dataset")

    df = df.drop_duplicates(
        subset=["id", "month_year"]
    ).copy()

    if df.empty:
        raise ValueError("The joined dataset contains no observations.")

    df["Long_Term_Nightly_Rent"] = df["Geometric Mean Rent"] / 7
    df["Price_Gap"] = df["price"] - df["Long_Term_Nightly_Rent"]

    return df


def summarise_price_gaps(df):
    """Summarise price gaps by location and apply the minimum sample rule."""

    summary = (
        df.dropna(subset=["Location Id", "Price_Gap"])
        .groupby("Location Id")
        .agg(
            Airbnb_Observations=("id", "count"),
            Median_Price_Gap=("Price_Gap", "median"),
            Mean_Price_Gap=("Price_Gap", "mean"),
            Maximum_Price_Gap=("Price_Gap", "max"),
            Minimum_Price_Gap=("Price_Gap", "min"),
        )
        .reset_index()
        .sort_values("Median_Price_Gap", ascending=False)
    )

    reliable = summary[
        summary["Airbnb_Observations"] >= MIN_OBSERVATIONS
    ].copy()

    if reliable.empty:
        raise ValueError(
            f"No locations have at least {MIN_OBSERVATIONS} observations."
        )

    return summary, reliable


def plot_price_gap_distribution(df):
    """Plot the overall price-gap distribution excluding extreme outliers."""

    q1 = df["Price_Gap"].quantile(0.25)
    q3 = df["Price_Gap"].quantile(0.75)
    iqr = q3 - q1

    lower_bound = q1 - OUTLIER_IQR_MULTIPLIER * iqr
    upper_bound = q3 + OUTLIER_IQR_MULTIPLIER * iqr

    plot_data = df[
        df["Price_Gap"].between(lower_bound, upper_bound)
    ]["Price_Gap"].dropna()

    plt.figure(figsize=(10, 6))
    plt.hist(plot_data, bins=HISTOGRAM_BINS, edgecolor="black")
    plt.axvline(0, linestyle="--", linewidth=1)
    plt.title(
        "Distribution of Airbnb vs Long-Term Rental Price Gaps\n"
        "(extreme outliers excluded from this chart)"
    )
    plt.xlabel("Price gap (NZD per night)")
    plt.ylabel("Number of Airbnb observations")
    plt.tight_layout()
    plt.show()


def plot_location_price_gaps(df, reliable_locations):
    """Plot price-gap distributions for the highest-median-gap locations."""

    location_order = reliable_locations.head(
        TOP_LOCATIONS_TO_PLOT
    )["Location Id"].tolist()

    plot_data = df[df["Location Id"].isin(location_order)]

    plot_values = [
        plot_data.loc[
            plot_data["Location Id"] == location_id,
            "Price_Gap",
        ].dropna().values
        for location_id in location_order
    ]

    plt.figure(figsize=(14, 8))
    plt.boxplot(
        plot_values,
        labels=[str(int(location_id)) for location_id in location_order],
        showfliers=False,
    )
    plt.axhline(0, linestyle="--", linewidth=1)
    plt.title(
        "Distribution of Airbnb vs Long-Term Rental Price Gaps\n"
        "Top 15 Locations by Median Gap"
    )
    plt.xlabel("Location ID")
    plt.ylabel("Price gap (NZD per night) — Airbnb − long-term rental")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def load_overall_bond_data(path):
    """Load overall rental-bond rows without double-counting categories."""

    bonds = pd.read_csv(path)
    validate_columns(bonds, REQUIRED_BOND_COLUMNS, "Rental-bond dataset")

    bonds_all = bonds[
        (bonds["Dwelling Type"] == "ALL")
        & (bonds["Number Of Beds"] == "ALL")
    ].copy()

    bonds_all["Location Id"] = pd.to_numeric(
        bonds_all["Location Id"], errors="coerce"
    ).astype("Int64")

    return bonds_all[bonds_all["Location Id"] != -99]


def calculate_property_counts(df, bonds_all):
    """Calculate Airbnb listing counts and rental-bond counts by location."""

    airbnb_counts = (
        df.dropna(subset=["Location Id"])
        .groupby("Location Id")
        .agg(Airbnb_Listings=("id", "nunique"))
        .reset_index()
    )

    rental_counts = (
        bonds_all
        .groupby("Location Id")
        .agg(
            Long_Term_Rental_Properties=(
                RENTAL_COUNT_COLUMN,
                "sum",
            )
        )
        .reset_index()
    )

    comparison = pd.merge(
        airbnb_counts,
        rental_counts,
        on="Location Id",
        how="outer",
    ).fillna(0)

    comparison["Airbnb_Listings"] = comparison["Airbnb_Listings"].astype(int)
    comparison["Long_Term_Rental_Properties"] = (
        comparison["Long_Term_Rental_Properties"].astype(int)
    )
    comparison["Total_Properties"] = (
        comparison["Airbnb_Listings"]
        + comparison["Long_Term_Rental_Properties"]
    )
    comparison["Airbnb_Percentage"] = (
        comparison["Airbnb_Listings"]
        / comparison["Total_Properties"]
        * 100
    )

    return comparison.sort_values("Airbnb_Listings", ascending=False)


def plot_property_counts(comparison):
    """Plot Airbnb and long-term rental counts for the largest Airbnb locations."""

    plot_data = (
        comparison[comparison["Airbnb_Listings"] > 0]
        .sort_values("Airbnb_Listings", ascending=False)
        .head(TOP_COUNT_LOCATIONS_TO_PLOT)
        .copy()
    )

    x = np.arange(len(plot_data))
    width = 0.38

    plt.figure(figsize=(10, max(6, len(plot_data) * 0.3)))
    plt.barh(
        x - width / 2,
        plot_data["Airbnb_Listings"],
        width,
        label="Airbnb listings",
    )
    plt.barh(
        x + width / 2,
        plot_data["Long_Term_Rental_Properties"],
        width,
        label="Long-term rental properties",
    )
    plt.yticks(
        x,
        [str(int(location_id)) for location_id in plot_data["Location Id"]],
    )
    plt.gca().invert_yaxis()
    plt.xlabel("Number of properties")
    plt.ylabel("Location ID")
    plt.title("Airbnb Listings vs Long-Term Rental Properties by Location")
    plt.legend()
    plt.tight_layout()
    plt.show()


def main():
    """Run the complete Deliverable 5 analysis."""

    df = load_joined_data(JOINED_INPUT)
    print(f"Number of rows after duplicate removal: {len(df)}")

    extreme_gaps = df[df["Price_Gap"] > 2000]
    if not extreme_gaps.empty:
        print("\nPrice gaps above NZ$2,000:")
        print(
            extreme_gaps[
                ["price", "Long_Term_Nightly_Rent", "Price_Gap"]
            ].to_string(index=False)
        )

    print("\nPrice-gap summary:")
    print(df["Price_Gap"].describe())

    plot_price_gap_distribution(df)

    location_gap_summary, reliable_locations = summarise_price_gaps(df)

    unreliable = location_gap_summary[
        location_gap_summary["Airbnb_Observations"] < MIN_OBSERVATIONS
    ]

    if not unreliable.empty:
        print(
            f"\nLocations with fewer than {MIN_OBSERVATIONS} observations:"
        )
        print(
            unreliable[
                ["Location Id", "Airbnb_Observations", "Median_Price_Gap"]
            ].to_string(index=False)
        )

    largest_gap_location = reliable_locations.iloc[0]

    print(
        f"\nLargest median price gap among locations with at least "
        f"{MIN_OBSERVATIONS} observations:"
    )
    print(f"Location ID: {int(largest_gap_location['Location Id'])}")
    print(
        f"Median price gap: "
        f"${largest_gap_location['Median_Price_Gap']:.2f} per night"
    )
    print(
        f"Mean price gap: "
        f"${largest_gap_location['Mean_Price_Gap']:.2f} per night"
    )
    print(
        f"Maximum observed gap: "
        f"${largest_gap_location['Maximum_Price_Gap']:.2f} per night"
    )

    plot_location_price_gaps(df, reliable_locations)

    bonds_all = load_overall_bond_data(BOND_INPUT)
    comparison = calculate_property_counts(df, bonds_all)

    print("\nLocation 322800:")
    print(comparison[comparison["Location Id"] == 322800].to_string(index=False))

    plot_property_counts(comparison)

    GAP_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    location_gap_summary.to_csv(GAP_OUTPUT, index=False)
    comparison.to_csv(COUNT_OUTPUT, index=False)

    print("\nResults saved successfully.")
    print(f"Price-gap summary: {GAP_OUTPUT}")
    print(f"Property-count comparison: {COUNT_OUTPUT}")


if __name__ == "__main__":
    main()
