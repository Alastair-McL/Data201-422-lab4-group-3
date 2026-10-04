.DEFAULT_GOAL := all

PYTHON ?= python

# Monthly Inside Airbnb files required by Deliverable 3.
MONTHLY_DATA := listings_2025_10.csv listings_2025_11.csv listings_2025_12.csv \
	listings_2026_01.csv listings_2026_02.csv listings_2026_03.csv \
	listings_2026_04.csv listings_2026_05.csv listings_2026_06.csv

DELIVERABLE_3_SCRIPT := deliverable_3 /airbnb_deliverable_3.py
DELIVERABLE_4_SCRIPT := deliverable_4/airbnb_deliverable_4.py
COMBINED_DATA := christchurch_listings_2025-10_to_2026-06.csv
D3_STAMP := .deliverable_3_complete
CLEANED_DATA := deliverable_5/christchurch_listings_cleaned.csv
CLEANING_NOTES := deliverable_5/deliverable_4_cleaning_notes.md

.PHONY: all deliverable_3 deliverable_4 area_codes clean

all: deliverable_4

# Deliverable 3 writes several outputs in one run, so use a stamp to record
# successful completion and avoid rerunning it when its inputs are unchanged.
$(D3_STAMP): $(MONTHLY_DATA) "$(DELIVERABLE_3_SCRIPT)"
	$(PYTHON) "$(DELIVERABLE_3_SCRIPT)"
	test -f "$(COMBINED_DATA)"
	touch "$@"

deliverable_3: $(D3_STAMP)

# Deliverable 4 uses the combined dataset and writes the cleaned data and notes.
$(CLEANED_DATA): $(D3_STAMP) "$(DELIVERABLE_4_SCRIPT)" | deliverable_5
	$(PYTHON) "$(DELIVERABLE_4_SCRIPT)" "$(COMBINED_DATA)" --output-dir deliverable_5
	test -f "$(CLEANING_NOTES)"

deliverable_4: $(CLEANED_DATA)

deliverable_5:
	mkdir -p deliverable_5

# Optional: requires KOORDINATES_API_KEY in the environment.
area_codes: deliverable_4
	@test -n "$$KOORDINATES_API_KEY" || (echo "Set KOORDINATES_API_KEY before running make area_codes" >&2; exit 1)
	$(PYTHON) deliverable_5/Stats_area_api_query.py

clean:
	rm -f "$(D3_STAMP)" "$(COMBINED_DATA)" "$(CLEANED_DATA)" "$(CLEANING_NOTES)"
