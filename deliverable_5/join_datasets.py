import pandas as pd

# Load datasets
airbnb = pd.read_csv(
    "deliverable_5/christchurch_listings_cleaned_area_codes.csv"
)

bonds = pd.read_csv(
    "deliverable_4/rental_bond_cleaned_filtered.csv"
)

# --------------------------------------------------
# 1. Convert Airbnb month to bond quarter
# --------------------------------------------------

airbnb["TimeFrame"] = (
    pd.to_datetime(airbnb["month_year"])
    .dt.to_period("Q")
    .dt.start_time
    .dt.strftime("%Y-%m-%d")
)

# --------------------------------------------------
# 2. Keep overall rental figures
# --------------------------------------------------

bonds_all = bonds[
    (bonds["Dwelling Type"] == "ALL") &
    (bonds["Number Of Beds"] == "ALL")
].copy()

# --------------------------------------------------
# 3. Make join columns the same data type
# --------------------------------------------------

airbnb["area_code"] = pd.to_numeric(
    airbnb["area_code"], errors="coerce"
).astype("Int64")

bonds_all["Location Id"] = pd.to_numeric(
    bonds_all["Location Id"], errors="coerce"
).astype("Int64")

# --------------------------------------------------
# 4. Check that bond join key is unique
# --------------------------------------------------

duplicates = bonds_all.duplicated(
    ["Location Id", "TimeFrame"]
).sum()

print("Duplicate bond keys:", duplicates)

# --------------------------------------------------
# 5. Join Airbnb and bond data
# --------------------------------------------------

merged = pd.merge(
    airbnb,
    bonds_all,
    left_on=["area_code", "TimeFrame"],
    right_on=["Location Id", "TimeFrame"],
    how="left"
)

# --------------------------------------------------
# 6. Save joined dataset
# --------------------------------------------------

output_file = (
    "deliverable_5/christchurch_airbnb_rental_joined.csv"
)

merged.to_csv(output_file, index=False)

# --------------------------------------------------
# 7. Check results
# --------------------------------------------------

print("Airbnb rows:", len(airbnb))
print("Joined rows:", len(merged))
print(
    "Rows with matching bond data:",
    merged["Location Id"].notna().sum()
)
print(
    "Rows without matching bond data:",
    merged["Location Id"].isna().sum()
)

print("\nSaved to:")
print(output_file)