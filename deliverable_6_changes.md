# Deliverable 6 – Coding Practice Changes

As part of Deliverable 6, the existing data pipeline was reviewed against the
coding practices covered in Week 9. This document records the substantial
changes made to the pipeline and the reasons for those changes.

---

# Deliverable 3 Changes

## Change 1: Improved Script Documentation and Readability

### Improved the file header

The file header was updated to more clearly describe the purpose, scope, and
outputs of the Deliverable 3 pipeline.

**From:**

```python
'''
Data201/422

AirBnB deliverable 3

Copy this file to a new folder that contains the combined Christchurch CSV file,
then run it from that folder.

Alastair McLauchlan
Sophie McNee
Darrel Susan Binu
Chinnu Rappai
'''
```

**To:**

```python
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
```

### Removed unused NumPy import

The NumPy import was removed because NumPy was not used anywhere in the Deliverable 3 script. This makes the dependencies clearer and avoids loading an unnecessary package.

**From:**

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
```

**To:**

```python
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
```

### Improved variable names

Generic variable names such as `df`, `christchurch`, and `combined` were replaced with more descriptive names, including:

- `monthly_listings`
- `christchurch_listings`
- `combined_listings`

**Why:** These changes make the script more self-documenting and easier for another user to understand, review, and maintain. Removing unused dependencies also makes it clearer which packages are actually required by the workflow.

---

## Change 2: Created a Central Parameter/Configuration Section

Key settings and assumptions were moved into a clearly defined parameter section near the top of the script.

The centralised parameters include:

```python
output_file = "christchurch_listings_2025-10_to_2026-06.csv"
price_plot_quantile = 0.99
identifier_columns = ["id", "host_id"]
category_columns = ["neighbourhood", "room_type", "month_year"]
review_plot_quantile = 0.99
top_reviewed_quantile = 0.90
scrape_date = "2026-06-19"
```

Hard-coded values within the processing and visualisation code were then replaced with the corresponding descriptive parameter names.

For example, rather than repeatedly using values such as `0.99` and `0.90` directly within the analysis, the script now refers to `price_plot_quantile`, `review_plot_quantile`, and `top_reviewed_quantile`.

**Why:** Centralising configurable parameters makes the assumptions underlying the analysis explicit and keeps important settings in one location. This makes the workflow easier to understand and modify without requiring a user to search throughout the processing code for hard-coded values.

---

## Change 3: Removed Duplicated and Unnecessary Processing

### Removed separate June 2026 processing

The original script contained a separate section that loaded, filtered, labelled, and saved the June 2026 Airbnb dataset:

```python
# Imported June 2026 data
df = pd.read_csv(folder / "listings_2026_06.csv")

print(df.head())
print("Rows and columns:", df.shape)
print("Column names:", df.columns.tolist())

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
```

This entire section was removed.

June 2026 was already included in the `input_files` dictionary and therefore processed through the same loop as the October 2025 to May 2026 datasets. The separate June processing duplicated work already being completed by the main workflow.


### Removed re-loading of the combined CSV

The following section was also removed:

```python
# Load the combined Christchurch dataset
combined = pd.read_csv(
    "christchurch_listings_2025-10_to_2026-06.csv"
)
```

The concatenated Christchurch dataset was already available in memory as `combined_listings`, so there was no need to save it and then immediately read the same data back into Python.

**Why:** Removing these sections reduces duplicated code and unnecessary file input/output. It also ensures that all nine monthly Airbnb datasets are prepared consistently through the same processing pipeline rather than treating June 2026 separately.

---

## Change 4: Corrected Output Paths and Project Organisation

A separate `output_folder` was defined based on the location of the Deliverable 3 script:

```python
folder = Path(__file__).parent.parent
output_folder = Path(__file__).parent
```

The two paths now have separate purposes:

- `folder` identifies the project root where the raw monthly Airbnb datasets are stored.
- `output_folder` identifies the `deliverable_3` folder where the outputs generated by the Deliverable 3 script should be stored.

The generated summary files were updated to save explicitly to `output_folder`, including:

- `missing_values_summary.csv`
- `numerical_summary.csv`
- `categorical_summary.csv`
- `category_counts.csv`

The generated visualisations were also updated to save to the Deliverable 3 folder, including:

- `christchurch_price_histogram.png`
- `days_since_last_review_histogram.png`

For example, output statements were changed to explicitly include the output directory:

```python
missing_summary.to_csv(
    output_folder / "missing_values_summary.csv"
)
```

and:

```python
plt.savefig(
    output_folder / "christchurch_price_histogram.png",
    dpi=300,
    bbox_inches="tight"
)
```

**Why:** Previously, some generated files were saved using relative filenames. This meant their location depended on the working directory from which the Python script was run and could result in duplicate outputs being created in the project root.

Defining `output_folder` makes the output location explicit and ensures that Deliverable 3 files are consistently stored together in the `deliverable_3` folder. This also ensures the workflow produces the same output locations regardless of the directory from which the script is run.

---

## Change 5: Ensured the Stored Dataset Represents the Final Processed Data

The point at which the combined Christchurch dataset is saved was changed.

Previously, the combined dataset was exported immediately after the nine monthly Christchurch datasets were concatenated. Further processing was then performed after the dataset had already been saved.

The save operation was moved until after the subsequent data-processing steps:

```python
# Save the final processed Christchurch dataset
combined_listings.to_csv(
    folder / output_file,
    index=False
)
```

The saved dataset therefore includes the later processing performed by the pipeline, including:

- conversion of the `price` variable to numeric;
- conversion of `last_review` to a date;
- addition and conversion of the `scrape_date`;
- calculation of `days_since_last_review`.

**Why:** Moving the export ensures that the stored CSV represents the final processed dataset produced by the workflow rather than an earlier intermediate version. This makes the saved dataset consistent with the data subsequently used by the analysis.

---

# Deliverable 4 Changes

Both airbnb_deliverable_4.py and rental_bond.py were checked against the Week 9 lecture on good coding habits. Below are the changes made:

---

# Part 1: Changes to airbnb_deliverable_4.py

## Change 1: Gave a variable a proper name

A column was just called c. Now it's called column.

**From:**

```python
for c in numeric_columns:
    original = df[c]
    ...
    log(f"Validate {c}", ...)
```

**To:**

```python
for column in numeric_columns:
    original = df[column]
    ...
    log(f"Validate {column}", ...)
```

**Why:** A good variable name tells what it is without needing a comment.

---

## Change 2: Put the key settings in one place

Some settings, like the expected months and the city name, were written directly inside the code. Moved them to the top of the file instead.

**From:**

```python
expected = pd.period_range("2025-10", "2026-06", freq="M").astype(str)
if not df.month_year.isin(expected).all() or not df.neighbourhood_group.eq("Christchurch City").all():
    raise ValueError("Unexpected month or city: inspect the input.")
```

**To:**

```python
EXPECTED_MONTH_START = "2025-10"
EXPECTED_MONTH_END = "2026-06"
EXPECTED_CITY = "Christchurch City"
DEFAULT_INPUT_FILENAME = "christchurch_listings_2025-10_to_2026-06.csv"
DEFAULT_OUTPUT_DIRNAME = "cleaned"
OUTPUT_CSV_NAME = "christchurch_listings_cleaned.csv"
OUTPUT_REPORT_NAME = "deliverable_4_cleaning_notes.md"
...
expected = pd.period_range(EXPECTED_MONTH_START, EXPECTED_MONTH_END, freq="M").astype(str)
if not df.month_year.isin(expected).all() or not df.neighbourhood_group.eq(EXPECTED_CITY).all():
    raise ValueError("Unexpected month or city: inspect the input.")
```

**Why:** It's easier to see all the settings in one spot at the top, instead of searching through the code to find them.

---

# Part 2: Changes to rental_bond.py

## Change 1: Added a description at the top

**From:**

```python
import pandas as pd


# ==================================================
# 1. Load the rental bond dataset
# ==================================================
```

**To:**

```python
"""
Deliverable 4: clean the rental bond dataset and filter it to the
October 2025 - June 2026 period used for the Airbnb comparison.

Reads the quarterly tenancy bond CSV, keeps the columns needed for
rental-price, property-count, dwelling-type and bedroom-category
analysis, validates identifiers and numeric ranges, and writes the
cleaned, filtered dataset to a new CSV.
"""
import argparse
from pathlib import Path
import pandas as pd
```

**Why:** So someone opening the file for the first time knows what it's for straight away.

---

## Change 2: Removed comments that just repeated the code

Some comments said the exact same thing as the line right after them, so these were taken out.

**From:**

```python
# Store Location Id as a nullable integer identifier.
filtered_bond_data["Location Id"] = (
    filtered_bond_data["Location Id"].astype("Int64")
)
...
# Display the data type of Number Of Beds.

print(
    filtered_bond_data["Number Of Beds"].dtype
)
```

**To:**

```python
filtered_bond_data["Location Id"] = filtered_bond_data["Location Id"].astype("Int64")
...
print(filtered_bond_data["Number Of Beds"].dtype)
```

Comments that explain a reason for a decision were kept, like why the value -99 is preserved, or why missing bed counts become "Unknown".
**Why:** A comment that just repeats the code isn't helping - it's extra words to read.

---

## Change 3: Put the key settings in one place

Settings like the filenames, the date range, and the column lists used to be scattered through the file, and some were even written twice. These were all moved to the top, in one spot, and the repeated copies were removed.

**From:**

```python
bond_file = "Detailed-Quarterly-Tenancy-Q1-2020-Q3-2026.csv"
bond_data = pd.read_csv(bond_file)
...
start_date = pd.Timestamp("2025-10-01")
end_date = pd.Timestamp("2026-06-30")
...
columns_to_keep = [
    "TimeFrame", "Location Id", "Dwelling Type", ...
]
...
output_file = "rental_bond_cleaned_filtered.csv"
```

**To:**

```python
DEFAULT_INPUT_FILENAME = "Detailed-Quarterly-Tenancy-Q1-2020-Q3-2026.csv"
DEFAULT_OUTPUT_FILENAME = "rental_bond_cleaned_filtered.csv"

START_DATE = pd.Timestamp("2025-10-01")
END_DATE = pd.Timestamp("2026-06-30")

COLUMNS_TO_KEEP = [
    "TimeFrame", "Location Id", "Dwelling Type", ...
]
```

**Why:** Now it's easy to see all the settings just by looking at the top of the file. It also used to be written in two places — that's risky, because if one copy gets changed and the other doesn't, they stop matching.

---

## Change 4: Made the code check its own assumptions

Two assumptions were only written down as comments. These were changed so the code checks them itself, and stops with an error if something looks wrong.

### Checking for negative Location Id values

**From:**

```python
# Location Id is an identifier and is retained.
# The value -99 is preserved because it may represent
# an unknown or special location category.
```

(the code didn't actually check this, it was just a comment)

**To:**

```python
KNOWN_SPECIAL_LOCATION_ID = -99
...
other_negative_location_ids = filtered_bond_data.loc[
    (filtered_bond_data["Location Id"] < 0)
    & (filtered_bond_data["Location Id"] != KNOWN_SPECIAL_LOCATION_ID),
    "Location Id",
].unique()
if len(other_negative_location_ids) > 0:
    raise ValueError(
        "Unexpected negative Location Id values found (not the known "
        f"special code {KNOWN_SPECIAL_LOCATION_ID}): {sorted(other_negative_location_ids)}"
    )
```

### Checking the data has the right time periods

**From:**

```python
# ==================================================
# 6. Filter the quarters from October 2025 to June 2026.
# This includes October 2025, January 2026, and April 2026.
# ==================================================
```

(again, just a comment - nothing in the code checked this)

**To:**

```python
EXPECTED_QUARTERS = [
    pd.Timestamp("2025-10-01"),
    pd.Timestamp("2026-01-01"),
    pd.Timestamp("2026-04-01"),
]
...
observed_quarters = sorted(filtered_bond_data["TimeFrame"].dropna().unique())
if list(observed_quarters) != EXPECTED_QUARTERS:
    raise ValueError(
        "Filtered data does not contain exactly the expected quarters "
        f"{[d.date() for d in EXPECTED_QUARTERS]}; found "
        f"{[pd.Timestamp(d).date() for d in observed_quarters]}. Inspect the source file."
    )
```

**Why:** A comment can be wrong and nobody would know. A check in the code shows an error right away if something isn't what was expected.

---

## Change 5: Gave the script a clear starting point

The script used to just run from top to bottom in one fixed way. It was rebuilt around one clear function

**From:**

```python
bond_file = "Detailed-Quarterly-Tenancy-Q1-2020-Q3-2026.csv"
bond_data = pd.read_csv(bond_file)
...
# (everything just runs top to bottom, step by step)
...
output_file = "rental_bond_cleaned_filtered.csv"
filtered_bond_data.to_csv(output_file, index=False)
```

**To:**

```python
def clean(source, output_file):
    source, output_file = Path(source), Path(output_file)
    bond_data = pd.read_csv(source)
    ...
    filtered_bond_data.to_csv(output_file, index=False)
    return filtered_bond_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", default=None)
    parser.add_argument("--output-file", default=None)
    args = parser.parse_args()

    script_folder = Path(__file__).parent
    input_file = Path(args.input) if args.input else script_folder / DEFAULT_INPUT_FILENAME
    output_path = Path(args.output_file) if args.output_file else script_folder / DEFAULT_OUTPUT_FILENAME

    clean(input_file, output_path)
```

**Why:** The script can now be reused on a different file, or tested, without opening it up and changing the code each time.

---

# Deliverable 5 Changes
