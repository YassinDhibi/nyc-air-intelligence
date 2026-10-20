"""Step 1: download and inspect NYC 2024 hourly PM2.5 *raw* measurements.

This script preserves the original monthly CSV files in data/monthly/ and
creates data/air_quality_2024.csv as a raw annual combination only when all
twelve source downloads succeed. It does not clean, filter, alter values, or
transform the measurements.
"""

from __future__ import annotations

from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

import pandas as pd


YEAR = 2024
BASE_URL = (
    "https://raw.githubusercontent.com/nychealth/nyccas-data/main/"
    "hist/csv/{year}/{month}.csv"
)
PROJECT_DIR = Path(__file__).resolve().parent
MONTHLY_DIR = PROJECT_DIR / "data" / "monthly"
# This is raw data. A later ETL step must write cleaned data to a separate file.
COMBINED_FILE = PROJECT_DIR / "data" / f"air_quality_{YEAR}.csv"
EXPECTED_COLUMNS = ["ID", "SiteID", "ObservationTimeUTC", "Value"]


def download_month(month: int) -> tuple[bool, str]:
    """Download one source file and validate its header before saving it."""
    url = BASE_URL.format(year=YEAR, month=month)
    destination = MONTHLY_DIR / f"air_quality_{YEAR}_{month:02d}.csv"
    temporary_file = destination.with_suffix(".part")

    try:
        with urlopen(url, timeout=30) as response:
            if response.status != 200:
                return False, f"HTTP {response.status}: {url}"
            content = response.read()
    except HTTPError as error:
        return False, f"HTTP {error.code}: {url}"
    except URLError as error:
        return False, f"Network error ({error.reason}): {url}"

    header = content.splitlines()[0].decode("utf-8-sig") if content else ""
    if header.split(",") != EXPECTED_COLUMNS:
        return False, f"Unexpected header {header!r}: {url}"

    temporary_file.write_bytes(content)
    temporary_file.replace(destination)
    return True, str(destination.relative_to(PROJECT_DIR))


def inspect_combined_data(combined: pd.DataFrame) -> None:
    """Print a read-only quality profile; do not change the raw dataframe."""
    # This temporary conversion is used only to report the date range and coverage.
    # The source column remains unchanged when the raw annual CSV is saved.
    timestamps = pd.to_datetime(combined["ObservationTimeUTC"], errors="coerce")
    months_present = sorted(timestamps.dropna().dt.month.unique().tolist())

    print("\nCombined dataset inspection")
    print(f"Rows: {len(combined):,}")
    print(f"Columns ({len(combined.columns)}): {list(combined.columns)}")
    print("Pandas-inferred data types (inspection only):")
    print(combined.dtypes.to_string())
    print(f"Date range: {timestamps.min()} to {timestamps.max()}")
    print("Missing values by column:")
    print(combined.isna().sum().to_string())
    print(f"Duplicate complete rows: {combined.duplicated().sum():,}")
    print(f"Months represented: {months_present}")
    print(f"All 12 months represented: {months_present == list(range(1, 13))}")


def main() -> None:
    MONTHLY_DIR.mkdir(parents=True, exist_ok=True)
    successful_months: list[int] = []
    failed_months: list[int] = []

    print("Downloading official NYC Health monthly CSV files for 2024...")
    for month in range(1, 13):
        success, message = download_month(month)
        if success:
            successful_months.append(month)
            print(f"Month {month:02d}: downloaded ({message})")
        else:
            failed_months.append(month)
            print(f"Month {month:02d}: FAILED - {message}")

    print(f"\nSuccessful months: {successful_months}")
    print(f"Failed months: {failed_months}")

    if failed_months:
        print("The annual CSV was not created because one or more downloads failed.")
        return

    monthly_files = [MONTHLY_DIR / f"air_quality_{YEAR}_{month:02d}.csv" for month in range(1, 13)]
    frames = [pd.read_csv(file) for file in monthly_files]
    combined = pd.concat(frames, ignore_index=True)
    combined.to_csv(COMBINED_FILE, index=False)
    print(f"\nCreated: {COMBINED_FILE.relative_to(PROJECT_DIR)}")
    inspect_combined_data(combined)


if __name__ == "__main__":
    main()
