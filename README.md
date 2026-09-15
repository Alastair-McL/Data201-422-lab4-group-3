# Data201-422-lab4-group-3
## AirBnB data dictionary
### This data is licensed under a Creative Commons Attribution 4.0 International License. CC BY 4.0
#### AirBnb NZ data sourced on 30th July 2026 from https://insideairbnb.com/get-the-data/
##### ID: unique identifier for the listing
##### Name: listing name
##### host_id: unique identifier for the host
##### host_name: host name
##### neighbourhood_group: larger regional area, such as district 
##### neighbourhood: smaller locality
##### latitude: latitude in WGS84 coordinate reference system 
##### longitude: longitude in WGS84 coordinate reference system
##### room_type: describes the room type with one of three options: Entire home/apt, Private room, or shared room
##### price: Price per night in NZD
##### minimum_nights: minimum numbers of nights that the room has to be booked for 
##### number_of_reviews: number of reviews the listing has received
##### last_review: Date of most recent review
##### reviews_per_month:  The average number of reviews per month the listing has received over the lifetime of the listing.
##### calculated_host_listings_count: number of reviews that the host has received across their collective listings 
##### availability_365: number of days in the next 365 that the listing is bookable for.
##### number_of_reviews_ltm: number of reviews the listing has received in the last 12 months 

# Detailed Quarterly Tenancy Data — Q1 2020 to Q3 2026

## Overview

This dataset (`Detailed-Quarterly-Tenancy-Q1-2020-Q3-2026.csv`) contains **quarterly residential tenancy bond and rent statistics for New Zealand**, broken down by location, dwelling type, and number of bedrooms.

The data is sourced from **rental bond lodgements**, which landlords/agents are legally required to register with **Tenancy Services** (part of the Ministry of Business, Innovation and Employment, MBIE) at the start of every tenancy under the Residential Tenancies Act. Because bond lodgement is compulsory, this dataset is considered one of the most complete administrative records of the private rental market in New Zealand (it does not, however, capture tenancies where no bond was lodged).

- **Publisher:** Tenancy Services / MBIE, New Zealand
- **Source page:** https://www.tenancy.govt.nz/about-tenancy-services/data-and-statistics/rental-bond-data/
- **Geography:** New Zealand — by location (suburb/territorial authority level)
- **Currency:** New Zealand Dollars (NZD)
- **Frequency:** Quarterly
- **Time span in this file:** Q1 2020 (1 Jan 2020) to Q3 2026 (1 Jul 2026), i.e. 26 quarterly snapshots
- **Rows in this file:** 226,080
- **Format:** CSV (UTF-8 with BOM), `\r\n` line endings

## Columns

| Column | Type | Description |
|---|---|---|
| `TimeFrame` | date | The start date of the quarter the row covers, in `YYYY-MM-DD` format (e.g. `2026-04-01` = the quarter from 1 Apr to 30 Jun 2026). All values fall on the 1st of Jan/Apr/Jul/Oct. |
| `Location Id` | code | A code identifying the location (suburb) the row relates to, as used in Tenancy Services' location reference table. Ordinary rows use a numeric location code (e.g. `100100`). Two special values are used for aggregate rows (see **Special location codes** below): `-99` (national/New Zealand-wide total) and `NULL` (bonds not attributable to a specific mapped location). |
| `Dwelling Type` | category | Type of rental dwelling. Observed values: `House`, `Flat`, `Apartment`, `Room`, `Boarding House`, and `ALL` (an aggregate across all dwelling types). |
| `Number Of Beds` | category | Number of bedrooms in the dwelling. Observed values: `0` (studio), `1`–`9`, `15`, `5+` (5 or more, used in some periods/locations instead of exact counts), `NA` (not recorded), and `ALL` (an aggregate across all bedroom counts). |
| `Total Bonds` | integer | Number of *new* bond lodgements recorded for this location/dwelling type/bed count combination during the quarter (i.e. new tenancies started). |
| `Active Bonds` | integer | Number of bonds that were held/active (in force) at any point during the quarter, for this combination — a broader, stock-style measure of tenancies rather than new lodgements. |
| `Closed Bonds` | integer | Number of bonds finalised/refunded (tenancies that ended) during the quarter, for this combination. |
| `Median Rent` | numeric (AUD/week) | Median weekly rent across the bonds/tenancies in this combination for the quarter. |
| `Geometric Mean Rent` | numeric (NZD/week) | Geometric mean of weekly rent — used because rent distributions are right-skewed; the geometric mean is less distorted by high-end outliers than the arithmetic mean. |
| `Upper Quartile Rent` | numeric (NZD/week) | The 75th percentile weekly rent for this combination. |
| `Lower Quartile Rent` | numeric (NZD/week) | The 25th percentile weekly rent for this combination. |
| `Log Std Dev Weekly Rent` | numeric | Standard deviation of the natural log of weekly rent — a measure of rent dispersion/inequality within the combination, consistent with reporting a geometric-mean-based rent series. |

### Notes on missing / null values

- Rent statistics (`Median Rent`, `Geometric Mean Rent`, `Upper Quartile Rent`, `Lower Quartile Rent`, `Log Std Dev Weekly Rent`) are recorded as the text `NULL` when there are too few bonds in a location/dwelling/bed combination for a quarter to calculate a reliable rent statistic (small-sample suppression), or where the row is one of the special aggregate rows described below.
- `Number Of Beds` = `NA` indicates the bedroom count was not recorded for that tenancy.

## Special location codes

- **`-99`** — a New Zealand–wide aggregate/total row (all locations combined), still broken down by `TimeFrame`, `Dwelling Type` and `Number Of Beds`.
- **`NULL`** — bonds that could not be matched to a specific location (e.g. an incomplete/unrecognised address), but were still counted toward national totals. These rows generally have populated `Total/Active/Closed Bonds` but `NULL` rent statistics.
- All other values are numeric **location codes**. This file does not include a lookup table mapping these codes to suburb/location names — Tenancy Services publishes that mapping separately as a location reference table alongside the bond data, and it would need to be joined in separately if location names are required.

## Row granularity

Each row represents one unique combination of:

`TimeFrame × Location Id × Dwelling Type × Number Of Beds`

For a given location and quarter, rows with `Dwelling Type = ALL` and/or `Number Of Beds = ALL` are pre-computed aggregates across the more granular rows — so summing "detailed" rows and the "ALL" rows together will double-count. Use either the granular rows *or* the `ALL` rows for a given analysis, not both.

## Suggested uses

- Tracking rent growth over time for a suburb, dwelling type, or bedroom count
- Comparing rental affordability/rent levels across New Zealand locations
- Analysing market activity (turnover) via `Total Bonds` / `Closed Bonds`
- Studying rent dispersion within a market using `Log Std Dev Weekly Rent`

## Caveats

- Reflects only tenancies with a **lodged rental bond**; excludes bond-free tenancies (rare) and most social/public housing.
- Rent figures are in NZD per week.
- Small-sample suppression means many suburb-level rows, especially for less common dwelling types or bedroom counts, will have `NULL` rent statistics even though bond counts are present.
- `Number Of Beds` coding is inconsistent across time (`5+` appears alongside exact values `5`–`15` in different periods), so treat it as an approximate/banded field for higher bedroom counts rather than a strictly continuous one.

