# ============================================================================
# # DATA201/422 – Christchurch Airbnb and Long-Term Rental Analysis

# ============================================================================
# ## 1. Import libraries
# ============================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



# ============================================================================
# ## 2. Load the joined Airbnb and rental-bond dataset
#
# This uses the joined dataset created in the previous task:
#
# `christchurch_airbnb_rental_joined.csv`
#
# The join was performed using `area_code` and `TimeFrame`, while retaining all Airbnb observations.
# ============================================================================

# Load the joined dataset

df = pd.read_csv(
    "deliverable_5/christchurch_airbnb_rental_joined.csv"
)

print("Number of rows:", len(df))
print("Number of columns:", len(df.columns))

df.head()



# ============================================================================
# ## 3. Check the important columns
#
# The following columns are required for this analysis:
#
# - `id` – Airbnb listing ID
# - `month_year` – Airbnb observation month
# - `price` – Airbnb nightly price
# - `Location Id` – Stats NZ location ID
# - `Geometric Mean Rent` – long-term rental weekly rent
#
# ============================================================================

required_columns = [
    "id",
    "month_year",
    "price",
    "Location Id",
    "Geometric Mean Rent"
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    print("Missing columns:", missing_columns)
else:
    print("All required columns are available.")



# ============================================================================
# ## 4. Remove duplicate Airbnb observations
#
# An Airbnb listing may occur more than once after joining with the rental-bond data. To ensure that each listing contributes once for each month, duplicates are removed using:
#
# `id + month_year`
#
# This prevents repeated joined rows from artificially affecting the price distribution.
# ============================================================================

df = df.drop_duplicates(
    subset=["id", "month_year"]
).copy()

print("Rows after removing duplicate listing-month observations:", len(df))



# ============================================================================
# ## 5. Convert long-term rent from weekly to nightly
#
# The rental-bond `Geometric Mean Rent` is a weekly amount.
#
# Therefore:
#
# **Long-term nightly equivalent = Geometric Mean Rent / 7**
#
# This makes it directly comparable with the Airbnb `price` column, which is a nightly price.
# ============================================================================

df["Long_Term_Nightly_Rent"] = (
    df["Geometric Mean Rent"] / 7
)

df[
    [
        "Geometric Mean Rent",
        "Long_Term_Nightly_Rent"
    ]
].head()



# ============================================================================
# # Question 1 – Largest short-term vs long-term rental price gap
#
# ## 6. Calculate the price gap for every Airbnb observation
#
# For every Airbnb listing:
#
# **Price gap = Airbnb nightly price − long-term nightly equivalent**
#
# A positive value means the Airbnb nightly price is higher than the equivalent long-term rental price.
#
# A negative value means the Airbnb nightly price is lower.
# ============================================================================

df["Price_Gap"] = (
    df["price"]
    - df["Long_Term_Nightly_Rent"]
)

print(df[df["Price_Gap"] > 2000][["price", "Long_Term_Nightly_Rent", "Price_Gap"]])

print("Price gap calculated for", df["Price_Gap"].notna().sum(), "observations.")



# ============================================================================
# ## 7. Inspect the price-gap distribution
#
# Before comparing locations, inspect the overall distribution and basic statistics.
# ============================================================================
print(df["Price_Gap"].describe())

q1 = df["Price_Gap"].quantile(0.25)
q3 = df["Price_Gap"].quantile(0.75)
iqr = q3 - q1

lower_bound = q1 - 3*iqr
upper_bound = q3 + 3*iqr

plot_data = df[
    (df["Price_Gap"] >= lower_bound) &
    (df["Price_Gap"] <= upper_bound)
]["Price_Gap"].dropna()

plt.figure(figsize=(10, 6))

plt.hist(
    plot_data,
    bins=50,
    edgecolor="black"
)

plt.axvline(
    0,
    linestyle="--",
    linewidth=1
)

plt.title(
    "Distribution of Airbnb vs Long-Term Rental Price Gaps\n"
    "(extreme outliers excluded from this chart)"
)

plt.xlabel(
    "Price gap (NZD per night)"
)

plt.ylabel(
    "Number of Airbnb observations"
)

plt.tight_layout()
plt.show()



# ============================================================================
# ## 8. Summarise the price gap by Location ID
#
# The median price gap is used as the main summary because it is less affected by unusually expensive Airbnb listings than the mean.
#
# The maximum and minimum gaps are also retained to show the range within each location.
# ============================================================================
location_gap_summary = (
    df.dropna(subset=["Location Id", "Price_Gap"])
    .groupby("Location Id")
    .agg(
        Airbnb_Observations=("id", "count"),
        Median_Price_Gap=("Price_Gap", "median"),
        Mean_Price_Gap=("Price_Gap", "mean"),
        Maximum_Price_Gap=("Price_Gap", "max"),
        Minimum_Price_Gap=("Price_Gap", "min")
    )
    .reset_index()
)

location_gap_summary = location_gap_summary.sort_values(
    "Median_Price_Gap",
    ascending=False
)

location_gap_summary.head(10)

# --------------------------------------------------------------------------
# Sanity check: restrict to locations with a reasonably reliable sample size
# --------------------------------------------------------------------------

MIN_OBSERVATIONS = 20

reliable_locations = location_gap_summary[
    location_gap_summary["Airbnb_Observations"] >= MIN_OBSERVATIONS
]

print(f"\nLocations with fewer than {MIN_OBSERVATIONS} Airbnb observations "
      f"(unreliable for median comparison):")
print(location_gap_summary[
    location_gap_summary["Airbnb_Observations"] < MIN_OBSERVATIONS
][["Location Id", "Airbnb_Observations", "Median_Price_Gap"]].to_string())

print(f"\nLargest median price gap among locations with at least "
      f"{MIN_OBSERVATIONS} Airbnb observations:")
print(reliable_locations.head(5).to_string())


# ============================================================================
# ## 9. Identify the location with the largest typical gap
#
# The location with the highest median price gap has the largest typical difference between Airbnb nightly prices and the long-term nightly rental equivalent.
#
# The table below provides the result to investigate further using the Stats NZ geographic lookup.
# ============================================================================

largest_gap_location = location_gap_summary.iloc[0]

print("Location ID with the largest median price gap:")
print(int(largest_gap_location["Location Id"]))

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



# ============================================================================
# ## 10. Plot the distribution of price gaps by Location ID
#
# A boxplot allows the distributions of price gaps to be compared across locations.
#
# To keep the chart readable, the 15 locations with the highest median price gaps are displayed.
# ============================================================================

top_gap_locations = (
    reliable_locations
    .head(15)["Location Id"]
    .tolist()
)

plot_gap_data = df[
    df["Location Id"].isin(top_gap_locations)
].copy()

# Order the locations by median price gap
location_order = (
    reliable_locations
    .head(15)["Location Id"]
    .tolist()
)

plot_values = [
    plot_gap_data.loc[
        plot_gap_data["Location Id"] == location_id,
        "Price_Gap"
    ].dropna().values
    for location_id in location_order
]

plt.figure(figsize=(14, 8))

plt.boxplot(
    plot_values,
    labels=[str(int(x)) for x in location_order],
    showfliers=False
)

plt.axhline(
    0,
    linestyle="--",
    linewidth=1
)

plt.title(
        "Distribution of Airbnb vs Long-Term Rental Price Gaps \n"
         "Top 15 Locations by Median Gap"
)

plt.xlabel("Location ID")
plt.ylabel(
    "Price gap (NZD per night)"
    "Airbnb − long-term rental"
)

plt.xticks(rotation=45)

plt.tight_layout()
plt.show()



# ============================================================================
# ### Interpreting Question 1
#
# The location with the highest **median price gap** represents the Christchurch area where the typical Airbnb nightly price is furthest above the equivalent long-term nightly rental price.
#
# Use the **Stats NZ Geographic Areas Table** to translate the resulting `Location Id` into the corresponding geographic/suburb name before writing the final conclusion.
# ============================================================================

# ============================================================================
# # Question 2 – Compare the number of Airbnb and long-term rental properties
#
# ## 11. Load the original rental-bond dataset
#
# For the property-count comparison, we use the rental-bond dataset directly.
#
# The `ALL` dwelling type and `ALL` number of beds filters retain the overall rental figures rather than individual dwelling-type/bed categories.
# ============================================================================

bonds = pd.read_csv(
    "deliverable_4/rental_bond_cleaned_filtered.csv"
)

print("Rental bond rows:", len(bonds))

print("\nRental bond columns:")
print(bonds.columns.tolist())



# ============================================================================
# ## 12. Keep the overall rental figures
# ============================================================================


bonds_all = bonds[
    (bonds["Dwelling Type"] == "ALL") &
    (bonds["Number Of Beds"] == "ALL")
].copy()

# Make Location Id numeric so it matches the joined Airbnb data
bonds_all["Location Id"] = pd.to_numeric(
    bonds_all["Location Id"],
    errors="coerce"
).astype("Int64")

# Exclude placeholder/unclassified location code
bonds_all = bonds_all[bonds_all["Location Id"] != -99]     # <-- ADD THIS LINE

print("Rows in overall rental dataset:", len(bonds_all))



# ============================================================================
# ## 13. Count Airbnb listings by location
#
# Airbnb listings are counted using unique listing IDs.
#
# This avoids counting the same Airbnb listing multiple times because it appears in different months.
# ============================================================================

airbnb_counts = (
    df.dropna(subset=["Location Id"])
    .groupby("Location Id")
    .agg(
        Airbnb_Listings=("id", "nunique")
    )
    .reset_index()
)

airbnb_counts.head()



# ============================================================================
# ## 14. Identify the rental-bond count column
#
# The rental-bond dataset may use a specific column name for the number of rental properties/bonds. The code below searches for likely count columns.
#
# Review the output and set `RENTAL_COUNT_COLUMN` to the correct column.
# ============================================================================

possible_count_columns = [
    column for column in bonds_all.columns
    if any(
        word in column.lower()
        for word in [
            "number",
            "count",
            "bond",
            "property"
        ]
    )
]

print("Possible rental count columns:")
print(possible_count_columns)



# --------------------------------------------------
# SET THIS AFTER CHECKING THE COLUMN LIST ABOVE
# --------------------------------------------------

# Example:
# RENTAL_COUNT_COLUMN = "Number Of Bonds"

RENTAL_COUNT_COLUMN = "Total Bonds"

if RENTAL_COUNT_COLUMN not in bonds_all.columns:
    raise KeyError(
        f"'{RENTAL_COUNT_COLUMN}' was not found. "
        "Check the printed column list and replace "
        "RENTAL_COUNT_COLUMN with the correct field name."
    )



# ============================================================================
# ## 15. Count long-term rental properties by location
#
# The overall rental-bond count is summed for each Location ID.
#
# If the rental-bond dataset contains multiple time periods, this produces the total across those periods. If your assignment requires a particular quarter or month, add that time filter before this aggregation.
# ============================================================================

rental_counts = (
    bonds_all
    .groupby("Location Id")
    .agg(
        Long_Term_Rental_Properties=(
            RENTAL_COUNT_COLUMN,
            "sum"
        )
    )
    .reset_index()
)

rental_counts.head()



# ============================================================================
# ## 16. Join Airbnb and long-term rental counts
#
# An outer join is used so that a location appearing in either dataset is retained.
# ============================================================================

comparison = pd.merge(
    airbnb_counts,
    rental_counts,
    on="Location Id",
    how="outer"
)

comparison[
    [
        "Airbnb_Listings",
        "Long_Term_Rental_Properties"
    ]
] = comparison[
    [
        "Airbnb_Listings",
        "Long_Term_Rental_Properties"
    ]
].fillna(0)

comparison["Airbnb_Listings"] = (
    comparison["Airbnb_Listings"].astype(int)
)

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

comparison = comparison.sort_values(
    "Airbnb_Listings",
    ascending=False
)

comparison.head(20)

print(comparison[comparison["Location Id"] == 322800]) 

# ============================================================================
# ## 17. Plot Airbnb listings vs long-term rental properties
#
# The chart below compares the number of Airbnb listings with the number of long-term rental properties for the locations with the largest combined number of properties.
# ============================================================================

top_locations = (
    comparison
    .sort_values(
        "Total_Properties",
        ascending=False
    )
    .head(15)
    .copy()
)

x = np.arange(len(top_locations))
width = 0.38

plt.figure(figsize=(14, 7))

plt.bar(
    x - width / 2,
    top_locations["Airbnb_Listings"],
    width,
    label="Airbnb listings"
)

plt.bar(
    x + width / 2,
    top_locations["Long_Term_Rental_Properties"],
    width,
    label="Long-term rental properties"
)

plt.xlabel("Location ID")
plt.ylabel("Number of properties")

plt.title(
    "Airbnb Listings vs Long-Term Rental Properties by Location"
)

plt.xticks(
    x,
    [str(int(x)) for x in top_locations["Location Id"]],
    rotation=45
)

plt.legend()

plt.tight_layout()
plt.show()



# ============================================================================
# ## 18. Save the results
#
# Saving the summary tables makes it easy to use them in the final report.
# ============================================================================

# Save Question 1 results
location_gap_summary.to_csv(
    "deliverable_5/location_price_gap_summary.csv",
    index=False
)

# Save Question 2 results
comparison.to_csv(
    "deliverable_5/airbnb_vs_long_term_rental_counts.csv",
    index=False
)

print("Results saved successfully.")



# ============================================================================
# # Final results to report
#
# After running the notebook:
#
# ### Question 1
# Report:
# - the `Location Id` with the highest median price gap;
# - the median gap in NZD per night;
# - the corresponding Christchurch geographic/suburb name using the Stats NZ Geographic Areas Table;
# - the boxplot showing the distribution of gaps.
#
# ### Question 2
# Report:
# - the number of Airbnb listings in each location;
# - the number of long-term rental properties in each location;
# - a comparison chart showing the differences.
#
# The numerical results should be taken directly from the generated tables rather than entered manually.
# ============================================================================
