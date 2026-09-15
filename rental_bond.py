import pandas as pd


# ==================================================
# 1. Load the rental bond dataset
# ==================================================

bond_file = "Detailed-Quarterly-Tenancy-Q1-2020-Q3-2026.csv"

bond_data = pd.read_csv(bond_file)

print("Rental bond dataset loaded successfully.")
print("Original dataset shape:", bond_data.shape)


# ==================================================
# 2. Display the original column names
# ==================================================

print("\nOriginal dataset columns:")
print(bond_data.columns.tolist())


# ==================================================
# 3. Display the original timeframe values
# ==================================================

print("\nOriginal timeframe values:")
print(bond_data["TimeFrame"].unique())


# ==================================================
# 4. Convert TimeFrame to datetime
# ==================================================

bond_data["TimeFrame"] = pd.to_datetime(
    bond_data["TimeFrame"],
    errors="coerce"
)

print("\nTimeFrame converted to datetime.")


# ==================================================
# 5. Check invalid timeframe values
# ==================================================

invalid_timeframes = bond_data["TimeFrame"].isna().sum()

print("\nInvalid timeframe values:")
print(invalid_timeframes)


# ==================================================
# 6. Filter the quarters from October 2025 to June 2026.
# This includes October 2025, January 2026, and April 2026.
# ==================================================

start_date = pd.Timestamp("2025-10-01")
end_date = pd.Timestamp("2026-06-30")

filtered_bond_data = bond_data[
    (bond_data["TimeFrame"] >= start_date) &
    (bond_data["TimeFrame"] <= end_date)
].copy()


# ==================================================
# 7. Display the number of rows for each timeframe
# ==================================================

print("\nNumber of rows for each timeframe:")

print(
    filtered_bond_data["TimeFrame"]
    .value_counts()
    .sort_index()
)

# ==================================================
# 8. Display the filtered dataset shape
# ==================================================

print("\nFiltered rental bond dataset shape:")
print(filtered_bond_data.shape)


# ==================================================
# 9. Check missing values before cleaning
# ==================================================

print("\nMissing values before cleaning:")
print(filtered_bond_data.isnull().sum())


# ==================================================
# 10. Select relevant columns
# ==================================================

# These columns are retained for rental-price,
# property-count, dwelling-type, and bedroom-category analysis.
#
# Location Id and TimeFrame are retained for identifying
# and comparing records over time.
#
# Dwelling Type is retained because it may distinguish
# different types of rental properties.

columns_to_keep = [
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
    "Log Std Dev Weekly Rent"
]


# Check whether all selected columns exist.

missing_columns = [
    column
    for column in columns_to_keep
    if column not in filtered_bond_data.columns
]

if missing_columns:
    raise KeyError(
        "The following columns are missing from the dataset: "
        + str(missing_columns)
    )


# Keep only the selected columns.

filtered_bond_data = filtered_bond_data[
    columns_to_keep
].copy()

print("\nColumns retained for analysis:")
print(filtered_bond_data.columns.tolist())


# ==================================================
# 11. Remove rows with missing essential identifiers
# ==================================================

rows_before_identifier_cleaning = len(filtered_bond_data)

filtered_bond_data = filtered_bond_data.dropna(
    subset=["Location Id", "TimeFrame"]
)

rows_removed = (
    rows_before_identifier_cleaning
    - len(filtered_bond_data)
)

print("\nRows removed because of missing identifiers:")
print(rows_removed)

print("\nShape after removing missing identifiers:")
print(filtered_bond_data.shape)


# ==================================================
# 12. Check and remove completely duplicated rows
# ==================================================

duplicate_count = filtered_bond_data.duplicated().sum()

print("\nCompletely duplicated rows found:")
print(duplicate_count)

filtered_bond_data = filtered_bond_data.drop_duplicates()

print("\nShape after removing duplicate rows:")
print(filtered_bond_data.shape)


# ==================================================
# 13. Convert numeric columns and handle Number Of Beds
# ==================================================

# Number Of Beds is kept as a categorical/string column.
# It contains values such as '5+' and 'ALL', which are
# not exact numeric values.
#
# Missing bed-category values are labelled as 'Unknown'
# because missing information does not mean zero beds.

numeric_columns = [
    "Location Id",
    "Total Bonds",
    "Active Bonds",
    "Closed Bonds",
    "Median Rent",
    "Geometric Mean Rent",
    "Upper Quartile Rent",
    "Lower Quartile Rent",
    "Log Std Dev Weekly Rent"
]


# Keep Number Of Beds as text/categorical data.
# Replace missing values with the category 'Unknown'.

filtered_bond_data["Number Of Beds"] = (
    filtered_bond_data["Number Of Beds"]
    .astype("string")
    .fillna("Unknown")
)


print("\nNumber Of Beds missing values after handling:")
print(
    filtered_bond_data["Number Of Beds"].isna().sum()
)


print("\nNumber Of Beds values:")
print(
    filtered_bond_data["Number Of Beds"]
    .value_counts(dropna=False)
    .sort_index()
)


# Convert only the genuinely numeric columns.

for column in numeric_columns:
    filtered_bond_data[column] = pd.to_numeric(
        filtered_bond_data[column],
        errors="coerce"
    )

# Store Location Id as a nullable integer identifier.
filtered_bond_data["Location Id"] = (
    filtered_bond_data["Location Id"].astype("Int64")
)

# Display the data type of Number Of Beds.

print("\nNumber Of Beds data type:")
print(
    filtered_bond_data["Number Of Beds"].dtype
)

# ==================================================
# 14. Check for invalid negative values
# ==================================================

# Location Id is an identifier and is retained.
# The value -99 is preserved because it may represent
# an unknown or special location category.
#
# Number Of Beds is categorical because it contains
# values such as '5+' and 'ALL'.
#
# Negative values are not expected for these
# numerical measurement columns.

non_negative_columns = [
    "Total Bonds",
    "Active Bonds",
    "Closed Bonds",
    "Median Rent",
    "Geometric Mean Rent",
    "Upper Quartile Rent",
    "Lower Quartile Rent",
    "Log Std Dev Weekly Rent"
]


for column in non_negative_columns:

    negative_count = (
        filtered_bond_data[column] < 0
    ).sum()

    print(
        f"Negative values in {column}:",
        negative_count
    )

    # Replace invalid negative values with missing values.

    filtered_bond_data.loc[
        filtered_bond_data[column] < 0,
        column
    ] = pd.NA


# ==================================================
# 15. Check the cleaned dataset
# ==================================================

print("\nMissing values after cleaning:")
print(
    filtered_bond_data.isnull().sum()
)

print("\nFinal cleaned dataset shape:")
print(
    filtered_bond_data.shape
)

print("\nFinal cleaned dataset preview:")
print(
    filtered_bond_data.head()
)


# ==================================================
# 16. Save the cleaned dataset
# ==================================================

output_file = "rental_bond_cleaned_filtered.csv"

filtered_bond_data.to_csv(
    output_file,
    index=False
)

print(
    "\nCleaned and filtered dataset saved successfully as:"
)

print(output_file)