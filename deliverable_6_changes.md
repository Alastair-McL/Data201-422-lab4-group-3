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

# Deliverable 5 Changes
