# Raw Airbnb source data

Download the monthly New Zealand `listings.csv` files from [Inside Airbnb](https://insideairbnb.com/get-the-data/).

- Deliverable 3 uses October 2025–June 2026.
- Deliverable 7 extends the period to August 2026.

Store the files locally in this folder using the naming pattern `listings_YYYY_MM.csv`, such as `listings_2025_10.csv`.

Use the summary `listings.csv` files, not `listings.csv.gz`.

The source CSVs are excluded from Git by `.gitignore`.
The preparation script filters each month to Christchurch City, adds the month and year, and combines the filtered records.

The combined Christchurch-only dataset is stored in the repository root:
[christchurch_listings_2025-10_to_2026-08.csv](../../christchurch_listings_2025-10_to_2026-08.csv).

Run pipeline commands from the repository root.