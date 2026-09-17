'''
replace "insert_your_api_key_here" with your actual Koordinates API key
save this file in the same directory as your input CSV file not github
replace input_file_path with the path to your input CSV file
replace output_file_path with the path where you want to save the output CSV file
uses 5 multiprocessing to speed up the queries
_______________________________________________
single test query to Koordinates API for one coordinate pair
import requests

api_key = "insert_your_api_key_here"
layer_id = 123515

latitude = -43.49815
longitude = 172.65054

url = "https://koordinates.com/services/query/v1/vector.json"

params = {
    "key": api_key,
    "layer": layer_id,
    "x": longitude,
    "y": latitude,
    "max_results": 1
}

response = requests.get(url, params=params)

print(response.status_code)
print(response.json())
'''
import requests
import pandas as pd
from pathlib import Path
from multiprocessing import Pool
import time

# Your existing Koordinates API key
API_KEY = "insert_your_api_key_here"

# Koordinates layer ID
LAYER_ID = 123515

# Input Airbnb CSV
INPUT_CSV = "/Users/alastairmclauchlan/HD documents/Uni/DATA201/airbnb/cleaned/christchurch_listings_cleaned.csv"

# Hard-coded output path
OUTPUT_CSV = "/Users/alastairmclauchlan/HD documents/Uni/DATA201/airbnb/cleaned/christchurch_listings_cleaned_area_codes.csv"

URL = "https://koordinates.com/services/query/v1/vector.json"


def get_area_code(coordinate):
    """Query Koordinates for one coordinate, retrying up to 3 times."""

    latitude, longitude = coordinate

    params = {
        "key": API_KEY,
        "layer": LAYER_ID,
        "x": longitude,
        "y": latitude,
        "max_results": 1
    }

    for attempt in range(1, 4):
        try:
            response = requests.get(URL, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()

                layer = data["vectorQuery"]["layers"][str(LAYER_ID)]
                features = layer["features"]

                if not features:
                    return coordinate, None

                area_code = features[0]["properties"]["SA22026_V1_00"]

                return coordinate, area_code

            print(
                f"API error for {latitude}, {longitude}: "
                f"status {response.status_code} "
                f"(attempt {attempt}/3)"
            )

        except requests.RequestException as error:
            print(
                f"Request failed for {latitude}, {longitude}: "
                f"{error} (attempt {attempt}/3)"
            )

        # Wait before retrying
        if attempt < 3:
            time.sleep(2)

    print(f"Giving up after 3 attempts: {latitude}, {longitude}")
    return coordinate, None


def main():
    # Read the full Airbnb dataset
    df = pd.read_csv(INPUT_CSV)

    print(f"Loaded {len(df)} Airbnb listings.")

    # Get unique latitude/longitude pairs
    coordinates = (
        df[["latitude", "longitude"]]
        .drop_duplicates()
        .itertuples(index=False, name=None)
    )

    coordinates = list(coordinates)

    print(f"Unique coordinate pairs: {len(coordinates)}")
    print(
        f"Duplicate coordinate rows avoided: "
        f"{len(df) - len(coordinates)}"
    )

    # Use exactly 5 processes
    processes = 5

    print(f"Using {processes} processes.")
    print("Starting Koordinates queries...")
    print("Failed requests will be retried up to 3 times.")

    with Pool(processes=processes) as pool:
        results = pool.map(get_area_code, coordinates)

    # Convert results into a dictionary
    area_codes = dict(results)

    # Add area codes to the full dataset
    df["area_code"] = [
        area_codes.get((latitude, longitude))
        for latitude, longitude in zip(df["latitude"], df["longitude"])
    ]

    # Save a copy of the full dataset
    df.to_csv(OUTPUT_CSV, index=False)

    print()
    print("Finished.")
    print(f"Total listings: {len(df)}")
    print(f"Unique coordinates queried: {len(coordinates)}")
    print(f"Listings with area codes: {df['area_code'].notna().sum()}")
    print(f"Listings without area codes: {df['area_code'].isna().sum()}")
    print()
    print("Saved to:")
    print(OUTPUT_CSV)


if __name__ == "__main__":
    main()
