'''Data201/422 
AirBnB deliverable 3
Alastair McLauchlan
Sophie Mcnee
Darrel Susan Binu
Chinnu Rappai
'''
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#Imported June 2026 data
df = pd.read_csv("listings_2026_06.csv")

print(df.head())
print("Rows and columns:", df.shape)
print("Column names:", df.columns.tolist())


import pandas as pd

# Load the full dataset
df = pd.read_csv("listings_2026_06.csv")

# Keep Christchurch City listings only
christchurch = df[
    df["neighbourhood_group"] == "Christchurch City"
].copy()

# Add the correct month and year
christchurch["month_year"] = "2026-06"

# Check the result
print(christchurch.head())
print("Original rows:", len(df))
print("Christchurch rows:", len(christchurch))

# Save the filtered dataset
christchurch.to_csv(
    "christchurch_listings_2026-06.csv",
    index=False
)


files = {
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

christchurch_datasets = []
#loading and filtering
for filename, month_year in files.items():
    df = pd.read_csv(filename)

    christchurch = df[
        df["neighbourhood_group"] == "Christchurch City"
    ].copy() 
    christchurch["month_year"] = month_year
    # Add it to the list of prepared datasets
    christchurch_datasets.append(christchurch)

    print(month_year, "Christchurch rows:", len(christchurch))

# Concatenate all nine prepared datasets
combined = pd.concat(christchurch_datasets, ignore_index=True)

# Save the combined dataset
combined.to_csv(
    "christchurch_listings_2025-10_to_2026-06.csv",
    index=False
)

print("Total combined rows:", len(combined))
print("Combined dataset saved successfully.")


# --------------------------------------------------
# SUMMARY STATISTICS
# --------------------------------------------------

# Missing values for every column
missing_summary = pd.DataFrame({
    "data_type": combined.dtypes.astype(str),
    "total_rows": len(combined),
    "non_missing": combined.notna().sum(),
    "missing": combined.isna().sum(),
    "missing_percent": (combined.isna().mean() * 100).round(2)
})

print("\nMISSING VALUES:")
print(missing_summary.to_string())
missing_summary.to_csv("missing_values_summary.csv")


# Numerical statistics
identifier_columns = ["id", "host_id"]

numerical_columns = combined.select_dtypes(
    include="number"
).columns.difference(identifier_columns)

numerical_summary = combined[numerical_columns].describe().T
numerical_summary = numerical_summary[
    ["count", "min", "max", "mean", "std"]
].round(2)

print("\nNUMERICAL SUMMARY:")
print(numerical_summary.to_string())
numerical_summary.to_csv("numerical_summary.csv")


# Categorical statistics
categorical_columns = combined.select_dtypes(
    include=["object", "category"]
).columns

categorical_summary = combined[categorical_columns].describe().T

categorical_summary = categorical_summary.rename(columns={
    "count": "non_missing_count",
    "unique": "number_of_categories",
    "top": "most_common_category",
    "freq": "most_common_count"
})

print("\nCATEGORICAL SUMMARY:")
print(categorical_summary.to_string())
categorical_summary.to_csv("categorical_summary.csv")


# Category counts
category_columns = ["neighbourhood", "room_type", "month_year"]
category_counts = []

for column in category_columns:
    counts = (
        combined[column]
        .value_counts(dropna=False)
        .rename_axis("category")
        .reset_index(name="count")
    )

    counts.insert(0, "column", column)
    category_counts.append(counts)

all_category_counts = pd.concat(category_counts, ignore_index=True)
all_category_counts.to_csv("category_counts.csv", index=False)

print("\nAll summary files saved successfully.")
