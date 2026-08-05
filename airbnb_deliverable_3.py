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
