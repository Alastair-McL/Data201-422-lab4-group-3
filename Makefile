.DEFAULT_GOAL := all

PYTHON ?= python

# Monthly Inside Airbnb files required by Deliverable 3.
MONTHLY_DATA := listings_2025_10.csv listings_2025_11.csv listings_2025_12.csv \
	listings_2026_01.csv listings_2026_02.csv listings_2026_03.csv \
	listings_2026_04.csv listings_2026_05.csv listings_2026_06.csv \
	listings_2026_07.csv listings_2026_08.csv

# The Deliverable 3 directory has a trailing space in its actual name.
DELIVERABLE_3_SCRIPT := deliverable_3 /airbnb_deliverable_3.py
DELIVERABLE_4_SCRIPT := deliverable_4/airbnb_deliverable_4.py
AREA_CODE_SCRIPT := deliverable_5/Stats_area_api_query.py
JOIN_SCRIPT := deliverable_5/join_datasets.py
ANALYSIS_SCRIPT := deliverable_5/christchurch_airbnb_rental_analysis.py

COMBINED_DATA := christchurch_listings_2025-10_to_2026-08.csv
D3_STAMP := .deliverable_3_complete
CLEANED_DATA := deliverable_5/christchurch_listings_cleaned.csv
CLEANING_NOTES := deliverable_5/deliverable_4_cleaning_notes.md
AREA_CODES_DATA := deliverable_5/christchurch_listings_cleaned_area_codes.csv
RENTAL_DATA := deliverable_4/rental_bond_cleaned_filtered.csv
JOINED_DATA := deliverable_5/christchurch_airbnb_rental_joined.csv
GAP_OUTPUT := deliverable_5/location_price_gap_summary.csv
COUNT_OUTPUT := deliverable_5/airbnb_vs_long_term_rental_counts.csv

.PHONY: all deliverable_3 deliverable_4 area_codes join analysis clean

all: analysis

# Do not list the Deliverable 3 script as a prerequisite: GNU Make treats
# quotes as literal characters in prerequisite names, and this directory
# name contains a space. Monthly files and this Makefile trigger regeneration.
$(D3_STAMP): $(MONTHLY_DATA) Makefile
	$(PYTHON) "$(DELIVERABLE_3_SCRIPT)"
	test -f "$(COMBINED_DATA)"
	touch "$@"

deliverable_3: $(D3_STAMP)

# Deliverable 4 runs after Deliverable 3 and writes the cleaned data and notes.
$(CLEANED_DATA): $(D3_STAMP) Makefile | deliverable_5
	$(PYTHON) "$(DELIVERABLE_4_SCRIPT)" "$(COMBINED_DATA)" --output-dir deliverable_5
	test -f "$(CLEANING_NOTES)"

deliverable_4: $(CLEANED_DATA)

deliverable_5:
	mkdir -p deliverable_5

# Requires KOORDINATES_API_KEY in the environment.
$(AREA_CODES_DATA): $(CLEANED_DATA) $(AREA_CODE_SCRIPT) Makefile
	@test -n "$$KOORDINATES_API_KEY" || (echo "Set KOORDINATES_API_KEY before running make area_codes" >&2; exit 1)
	$(PYTHON) "$(AREA_CODE_SCRIPT)"
	test -f "$(AREA_CODES_DATA)"

area_codes: $(AREA_CODES_DATA)

# Join Airbnb data to the rental-bond data.
$(JOINED_DATA): $(AREA_CODES_DATA) $(RENTAL_DATA) $(JOIN_SCRIPT) Makefile
	$(PYTHON) "$(JOIN_SCRIPT)"
	test -f "$(JOINED_DATA)"

join: $(JOINED_DATA)

# Deliverable 5 analysis produces both CSV result files and displays the plots.
$(GAP_OUTPUT) $(COUNT_OUTPUT): $(JOINED_DATA) $(RENTAL_DATA) $(ANALYSIS_SCRIPT) Makefile
	$(PYTHON) "$(ANALYSIS_SCRIPT)"
	test -f "$(GAP_OUTPUT)"
	test -f "$(COUNT_OUTPUT)"

analysis: $(GAP_OUTPUT) $(COUNT_OUTPUT)

clean:
	rm -f "$(D3_STAMP)" "$(COMBINED_DATA)" "$(CLEANED_DATA)" "$(CLEANING_NOTES)" \
		"$(AREA_CODES_DATA)" "$(JOINED_DATA)" "$(GAP_OUTPUT)" "$(COUNT_OUTPUT)"
