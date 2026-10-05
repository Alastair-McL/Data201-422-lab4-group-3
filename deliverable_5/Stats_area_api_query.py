"""Add Stats NZ area codes to Christchurch Airbnb listings.

The script uses the Koordinates API to find the Stats NZ area code for each
unique Airbnb coordinate pair. Set KOORDINATES_API_KEY in the environment
before running the script.
"""

import os
import time
from multiprocessing import Pool
from pathlib import Path

import pandas as pd
import requests


API_URL = "https://koordinates.com/services/query/v1/vector.json"
LAYER_ID = 123515
AREA_CODE_FIELD = "SA22026_V1_00"
API_KEY_ENV_VAR = "KOORDINATES_API_KEY"

INPUT_CSV = Path("deliverable_5/christchurch_listings_cleaned.csv")
OUTPUT_CSV = Path("deliverable_5/christchurch_listings_cleaned_area_codes.csv")

REQUEST_TIMEOUT = 30
MAX_RETRIES = 5
RETRY_DELAY_SECONDS = 5
PROCESS_COUNT = 1
MAX_RESULTS = 1


def get_area_code(coordinate):
    """Return the Stats NZ area code for one latitude/longitude pair."""

    latitude, longitude = coordinate
    api_key = os.environ[API_KEY_ENV_VAR]

    params = {
        "key": api_key,
        "layer": LAYER_ID,
        "x": longitude,
        "y": latitude,
        "max_results": MAX_RESULTS,
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(
                API_URL,
                params=params,
                timeout=REQUEST_TIMEOUT,
            )

            if response.status_code == 200:
                data = response.json()
                layer = data["vectorQuery"]["layers"][str(LAYER_ID)]
                features = layer["features"]

                if not features:
                    return coordinate, None

                return coordinate, features[0]["properties"][AREA_CODE_FIELD]

            print(
                f"API error for {latitude}, {longitude}: "
                f"status {response.status_code} "
                f"(attempt {attempt}/{MAX_RETRIES})"
            )

        except (requests.RequestException, KeyError, ValueError) as error:
            print(
                f"Request failed for {latitude}, {longitude}: "
                f"{error} (attempt {attempt}/{MAX_RETRIES})"
            )

        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY_SECONDS)

    print(f"Giving up after {MAX_RETRIES} attempts: {latitude}, {longitude}")
    return coordinate, None


def load_coordinates(input_path):
    """Load the Airbnb data and return the dataframe and unique coordinates."""

    df = pd.read_csv(input_path)

    required_columns = {"latitude", "longitude"}
    missing_columns = required_columns.difference(df.columns)
    if missing_columns:
        raise ValueError(
            f"Input file is missing required columns: {sorted(missing_columns)}"
        )

    coordinates = list(
        df[["latitude", "longitude"]]
        .drop_duplicates()
        .itertuples(index=False, name=None)
    )

    return df, coordinates


def main():
    """Query Koordinates and save the Airbnb data with area codes."""

    if not os.environ.get(API_KEY_ENV_VAR):
        raise RuntimeError(
            f"Set {API_KEY_ENV_VAR} in your environment before running this script."
        )

    df, coordinates = load_coordinates(INPUT_CSV)

    print(f"Loaded {len(df)} Airbnb listings.")
    print(f"Unique coordinate pairs: {len(coordinates)}")
    print(f"Duplicate coordinate rows avoided: {len(df) - len(coordinates)}")
    print(f"Using {PROCESS_COUNT} processes.")
    print(
        f"Starting Koordinates queries with up to {MAX_RETRIES} "
        f"attempts per request..."
    )

    with Pool(processes=PROCESS_COUNT) as pool:
        results = pool.map(get_area_code, coordinates)

    area_codes = dict(results)
    df["area_code"] = [
        area_codes.get((latitude, longitude))
        for latitude, longitude in zip(df["latitude"], df["longitude"])
    ]

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)

    missing_area_codes = df["area_code"].isna().sum()

    print("\nFinished.")
    print(f"Total listings: {len(df)}")
    print(f"Unique coordinates queried: {len(coordinates)}")
    print(f"Listings with area codes: {len(df) - missing_area_codes}")
    print(f"Listings without area codes: {missing_area_codes}")
    print(f"Saved to: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
