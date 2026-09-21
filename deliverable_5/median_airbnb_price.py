import pandas as pd

# Load the joined Airbnb and rental bond dataset
df = pd.read_csv("deliverable_5/christchurch_airbnb_rental_joined.csv")

# Filter for Christchurch Central (Location ID 326600)
christchurch_central = df[df["Location Id"] == 326600]

# Remove duplicate Airbnb observations created by the join
christchurch_central = christchurch_central.drop_duplicates(
    subset=["id", "month_year"]
)

# Calculate the median nightly Airbnb price
median_price = christchurch_central["price"].median()

print(f"Median Airbnb price in Christchurch Central: ${median_price:.2f}")