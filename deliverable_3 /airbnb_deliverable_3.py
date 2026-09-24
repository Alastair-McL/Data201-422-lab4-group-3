'''
Data201/422 - Deliverable 3 - AirBnB Christchurch Data Analysis

Processes Airbnb listings from October 2025 to June 2026. 
Filters the data to Christchurch City listings only, combines the monthly datasets, 
and produces summary statistics and visualisations.

Authors: 
Alastair McLauchlan
Sophie McNee
Darrel Susan Binu
Chinnu Rappai
'''

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

"""set working folder"""
# Find the folder where this Python script is located.
# This prevents problems caused by running the script from another directory.
folder = Path(__file__).parent.parent
output_folder = Path(__file__).parent

input_files = {
    "listings_2025_10.csv": "2025-10",
    "listings_2025_11.csv": "2025-11",
    "listings_2025_12.csv": "2025-12",
    "listings_2026_01.csv": "2026-01",
    "listings_2026_02.csv": "2026-02",
    "listings_2026_03.csv": "2026-03",
    "listings_2026_04.csv": "2026-04",
    "listings_2026_05.csv": "2026-05",
    "listings_2026_06.csv": "2026-06"
}
output_file = "christchurch_listings_2025-10_to_2026-06.csv"
price_plot_quantile = 0.99
identifier_columns = ["id", "host_id"]
category_columns = ["neighbourhood", "room_type", "month_year"]
review_plot_quantile = 0.99
top_reviewed_quantile = 0.90
scrape_date = "2026-06-19"

christchurch_datasets = []
#loading and filtering
for filename, month_year in input_files.items():
    monthly_listings = pd.read_csv(folder/filename)

    christchurch_listings = monthly_listings[
        monthly_listings["neighbourhood_group"] == "Christchurch City"
    ].copy() 
    christchurch_listings["month_year"] = month_year
    # Add it to the list of prepared datasets
    christchurch_datasets.append(christchurch_listings)

    print(month_year, "Christchurch rows:", len(christchurch_listings))

# Concatenate all nine prepared datasets
combined_listings = pd.concat(
    christchurch_datasets, 
    ignore_index=True
    )


# Convert price to numeric
combined_listings["price"] = pd.to_numeric(
    combined_listings["price"]
    .astype(str)
    .str.replace("$", "", regex=False)
    .str.replace(",", "", regex=False),
    errors="coerce"
)

# Remove missing prices only from the data used for plotting
christchurch_prices = combined_listings["price"].dropna()

print("Listings with a valid price:", len(christchurch_prices))
print("Listings with a missing price:", combined_listings["price"].isna().sum())


# Limit the displayed range to the 99th percentile
# This prevents extreme prices from compressing the histogram
price_limit = christchurch_prices.quantile(price_plot_quantile)


# --------------------------------------------------
# SUMMARY STATISTICS
# --------------------------------------------------

# Missing values for every column
missing_summary = pd.DataFrame({
    "data_type": combined_listings.dtypes.astype(str),
    "total_rows": len(combined_listings),
    "non_missing": combined_listings.notna().sum(),
    "missing": combined_listings.isna().sum(),
    "missing_percent": (combined_listings.isna().mean() * 100).round(2)
})

print("\nMISSING VALUES:")
print(missing_summary.to_string())
missing_summary.to_csv(
    output_folder / "missing_values_summary.csv"
)

# Numerical statistics
numerical_columns = combined_listings.select_dtypes(
    include="number"
).columns.difference(identifier_columns)

numerical_summary = combined_listings[numerical_columns].describe().T
numerical_summary = numerical_summary[
    ["count", "min", "max", "mean", "std"]
].round(2)

print("\nNUMERICAL SUMMARY:")
print(numerical_summary.to_string())
numerical_summary.to_csv(
    output_folder / "numerical_summary.csv"
)


# Categorical statistics
categorical_columns = combined_listings.select_dtypes(
    include=["object", "category"]
).columns

categorical_summary = combined_listings[categorical_columns].describe().T

categorical_summary = categorical_summary.rename(columns={
    "count": "non_missing_count",
    "unique": "number_of_categories",
    "top": "most_common_category",
    "freq": "most_common_count"
})

print("\nCATEGORICAL SUMMARY:")
print(categorical_summary.to_string())
categorical_summary.to_csv(
    output_folder / "categorical_summary.csv"
)

# Category counts
category_counts = []

for column in category_columns:
    counts = (
        combined_listings[column]
        .value_counts(dropna=False)
        .rename_axis("category")
        .reset_index(name="count")
    )

    counts.insert(0, "column", column)
    category_counts.append(counts)

all_category_counts = pd.concat(category_counts, ignore_index=True)
all_category_counts.to_csv(
    output_folder / "category_counts.csv",
    index=False
)
print("\nAll summary files saved successfully.")

# --------------------------------------------------
# Visualisations
# --------------------------------------------------
# Plot the price histogram
# Retain valid, non-negative prices
christchurch_prices = combined_listings.loc[
    combined_listings["price"].notna()
    & (combined_listings["price"] >= 0),
    "price"
]

# --- Plot 1 Christchurch Price Histogram ---
plt.figure(figsize=(10, 6))

plt.hist(
    christchurch_prices,
    bins=50,
    range=(0, price_limit),
    color="steelblue",
    edgecolor="black",
    alpha=0.8
)

plt.title(
    "Christchurch Airbnb Price Distribution\n"
    "October 2025–June 2026"
)
plt.xlabel("Price per night (NZD)")
plt.ylabel("Number of listing records")
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()

# Save the plot before displaying it
plt.savefig(
    output_folder / "christchurch_price_histogram.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# --------------------------------------------------
# Plot 2 -Days Since Last Review Histogram
# --------------------------------------------------

# Add scrape date (same as KNIME workflow)
combined_listings["scrape_date"] = scrape_date

# Convert dates
combined_listings["scrape_date"] = pd.to_datetime(
    combined_listings["scrape_date"]
)

combined_listings["last_review"] = pd.to_datetime(
    combined_listings["last_review"],
    errors="coerce"
)

# Calculate days since last review
combined_listings["days_since_last_review"] = (
    combined_listings["scrape_date"] - combined_listings["last_review"]
).dt.days

# Save the final processed Christchurch dataset
combined_listings.to_csv(
    folder / output_file,
    index=False
)

print("Total combined rows:", len(combined_listings))
print("Final combined dataset saved successfully.")

# Remove missing and invalid values
days_since_review = combined_listings[
    combined_listings["days_since_last_review"].notna()
    & (combined_listings["days_since_last_review"] >= 0)
]["days_since_last_review"]


print("Listings with valid review dates:", len(days_since_review))
print("Missing review dates:", combined_listings["last_review"].isna().sum())


# Remove extreme values for visualisation
review_limit = days_since_review.quantile(review_plot_quantile)


# Plot histogram
plt.figure(figsize=(10, 6))

plt.hist(
    days_since_review[days_since_review <= review_limit],
    bins=50,
    range=(0, review_limit),
    edgecolor="black",
    alpha=0.8
)

plt.title(
    "Distribution of Days Since Last Review\n"
    "Christchurch Airbnb Listings (October 2025–June 2026)"
)

plt.xlabel("Days Since Last Review")
plt.ylabel("Number of Listing Records")

plt.grid(axis="y", alpha=0.3)

plt.tight_layout()

plt.savefig(
    output_folder / "days_since_last_review_histogram.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# --------------------------------------------------
# Top 10% Most Reviewed Properties in Christchurch
# --------------------------------------------------

# Find the review count threshold for the top 10%
review_threshold = combined_listings["number_of_reviews"].quantile(top_reviewed_quantile)

print("Top 10% review threshold:", review_threshold)

# Filter properties in the top 10%
top_reviewed = combined_listings[
    combined_listings["number_of_reviews"] >= review_threshold
].copy()

print(
    "Number of top 10% reviewed properties in Christchurch:",
    len(top_reviewed)
)

# Display the top 10 most reviewed Christchurch properties
print(
    top_reviewed[
        [
            "id",
            "name",
            "number_of_reviews",
            "neighbourhood_group",
            "room_type"
        ]
    ]
    .sort_values(
        by="number_of_reviews",
        ascending=False
    )
    .head(10)
)