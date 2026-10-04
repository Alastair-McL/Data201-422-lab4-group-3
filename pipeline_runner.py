"""Run the reproducible Airbnb data pipeline from the repository root.

Default run:
  1. Build the combined Christchurch dataset and Deliverable 3 summaries.
  2. Clean the combined dataset with Deliverable 4 and save it under deliverable_5/.

Optional:
  --with-api also queries Koordinates for Stats NZ area codes. This requires
  KOORDINATES_API_KEY and makes external API requests.
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DELIVERABLE_3 = ROOT / "deliverable_3 " / "airbnb_deliverable_3.py"
DELIVERABLE_4 = ROOT / "deliverable_4" / "airbnb_deliverable_4.py"
DELIVERABLE_5_API = ROOT / "deliverable_5" / "Stats_area_api_query.py"
COMBINED_CSV = ROOT / "christchurch_listings_2025-10_to_2026-06.csv"
CLEANED_OUTPUT_DIR = ROOT / "deliverable_5"


def run_step(label, command, *, cwd=ROOT, env=None):
    """Run one pipeline step and stop immediately if it fails."""
    print(f"\n{'=' * 72}\n{label}\n{'=' * 72}", flush=True)
    subprocess.run(command, cwd=cwd, env=env, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--with-api",
        action="store_true",
        help="also query Koordinates for Stats NZ area codes (requires an API key)",
    )
    args = parser.parse_args()

    required = [
        DELIVERABLE_3,
        DELIVERABLE_4,
        *[
            ROOT / f"listings_{year}_{month:02d}.csv"
            for year, months in [(2025, range(10, 13)), (2026, range(1, 7))]
            for month in months
        ],
    ]
    missing = [path for path in required if not path.is_file()]
    if missing:
        print("Pipeline cannot start; required files are missing:", file=sys.stderr)
        for path in missing:
            print(f"  - {path.relative_to(ROOT)}", file=sys.stderr)
        return 1

    run_step(
        "Step 1/2: Deliverable 3 — combine monthly data and create summaries",
        [sys.executable, str(DELIVERABLE_3)],
    )

    if not COMBINED_CSV.is_file():
        print(f"Expected combined dataset was not created: {COMBINED_CSV}", file=sys.stderr)
        return 1

    run_step(
        "Step 2/2: Deliverable 4 — clean the combined Christchurch dataset",
        [
            sys.executable,
            str(DELIVERABLE_4),
            str(COMBINED_CSV),
            "--output-dir",
            str(CLEANED_OUTPUT_DIR),
        ],
    )

    if args.with_api:
        if not os.environ.get("KOORDINATES_API_KEY"):
            print(
                "The --with-api option requires KOORDINATES_API_KEY to be set "
                "in your environment. The local steps have completed.",
                file=sys.stderr,
            )
            return 2
        run_step(
            "Optional step: query Koordinates for Stats NZ area codes",
            [sys.executable, str(DELIVERABLE_5_API)],
        )

    print("\nPipeline completed successfully.", flush=True)
    if not args.with_api:
        print(
            "The Koordinates API step was skipped. Run with --with-api "
            "when KOORDINATES_API_KEY is configured."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
