import logging
import mariadb
import openpyxl
from dotenv import load_dotenv
from openpyxl.worksheet.worksheet import Worksheet

import argparse
import os
import sys
from datetime import date
from pathlib import Path
from typing import Any

from model import Result
from queries import RESULTS_QUERY

load_dotenv()

DATE_FORMAT = "%Y-%m-%d"
BASE_XLS_FILE = Path("input") / "Rankinglijst.xlsm"
XLS_WORKSHEET = "Resultaten"
XLS_DATE_CELL = "E5"
XLS_CONTENT_START_ROW = 9
OUTPUT_FOLDER = Path("output")

MARIADB_USER = os.getenv("MARIADB_USER")
MARIADB_PASSWORD = os.getenv("MARIADB_PASSWORD")
MARIADB_HOST = os.getenv("MARIADB_HOST")
MARIADB_PORT = int(os.getenv("MARIADB_PORT", "3306"))
MARIADB_DATABASE = os.getenv("MARIADB_DATABASE")

logger = logging.getLogger(__name__)


# Connect to MariaDB Platform
try:
    conn = mariadb.connect(
        user=MARIADB_USER,
        password=MARIADB_PASSWORD,
        host=MARIADB_HOST,
        port=MARIADB_PORT,
        database=MARIADB_DATABASE
    )

except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)


def get_results_per_discipline(day: date) -> dict[str, list[Result]]:
    """
    Queries the database and returns the results per discipline for the given day
    """

    date_str = day.strftime(DATE_FORMAT)

    cur = conn.cursor()
    cur.execute(RESULTS_QUERY, (date_str + "%",))
    results = [Result(*row) for row in cur.fetchall()]

    results_per_discipline: dict[str, list[Result]] = {}
    for r in results:
        if r.discipline not in results_per_discipline:
            results_per_discipline[r.discipline] = []
        results_per_discipline[r.discipline].append(r)

    return results_per_discipline


def insert_row_into_worksheet(
    worksheet: Worksheet,
    row: int,
    values: tuple[Any],
):
    """
    Inserts a group of values into the given row in the given Excel worksheet
    """

    for i, val in enumerate(values):
        col = chr(ord('@')+i+1)
        cell = f"{col}{row}"
        worksheet[cell] = val


def add_results_to_worksheet(
    results_per_discipline: dict[str, list[Result]],
    worksheet: Worksheet,
    starting_row: int,
):
    """
    Inserts the given results (grouped by discipline) into the given Excel worksheet.
    Inserted results are grouped by discipline and sorted by total score and inner tens
    within each group
    """

    curr_row = starting_row
    for _, results in results_per_discipline.items():
        # Sort by total, and then by inner tens
        results.sort(key=lambda r: (r.total, r.inner_tens), reverse=True)
        for i, row in enumerate(results):
            values = (
                i+1,
                row.discipline,
                "-",
                "-",
                row.sport_pass_id,
                row.full_name,
                row.club_id,
                row.club,
                row.series1,
                row.series2,
                row.series3,
                "",
                "",
                "",
                row.inner_tens,
                row.rounded_total,
            )
            insert_row_into_worksheet(worksheet, curr_row, values)
            curr_row += 1
    

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "--date",
        type=lambda s: date.strptime(s, DATE_FORMAT),
        default=date.today(),
        help="The tournament date for which to fetch results."
    )
    args = argparser.parse_args()

    day: date = args.date
    date_str = day.strftime(DATE_FORMAT)
    # Get the results per discipline from the Meyton database
    results_per_discipline = get_results_per_discipline(day)

    # Load Excel worksheet that's used as a base
    workbook = openpyxl.load_workbook(BASE_XLS_FILE)
    worksheet = workbook[XLS_WORKSHEET]
    # Update dynamic worksheet metadata
    worksheet[XLS_DATE_CELL] = f"{day.month}/{day.day}/{day.year}"
    # Add results to Excel worksheet
    add_results_to_worksheet(results_per_discipline, worksheet, XLS_CONTENT_START_ROW)
    # Store the updated Excel workbook in the output folder
    OUTPUT_FOLDER.mkdir(exist_ok=True)
    workbook.save(OUTPUT_FOLDER / f'{BASE_XLS_FILE.stem}-{date_str}.xlsx')
