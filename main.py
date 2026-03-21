import mariadb
import openpyxl
from dotenv import load_dotenv

import argparse
import csv
import os
import sys
from datetime import date
from pathlib import Path

from model import Result
from queries import RESULTS_QUERY

load_dotenv()

DATE_FORMAT = "%Y-%m-%d"
OUTPUT_FOLDER = Path("output")

MARIADB_USER = os.getenv("MARIADB_USER")
MARIADB_PASSWORD = os.getenv("MARIADB_PASSWORD")
MARIADB_HOST = os.getenv("MARIADB_HOST")
MARIADB_PORT = int(os.getenv("MARIADB_PORT", "3306"))
MARIADB_DATABASE = os.getenv("MARIADB_DATABASE")


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


def save_tournament_results_for_day(day: date):
    # Get Cursor
    cur = conn.cursor()

    date_str = day.strftime(DATE_FORMAT)

    cur.execute(RESULTS_QUERY, (date_str + "%",))
    rows = [Result(*row) for row in cur.fetchall()]

    rows_per_discipline: dict[str, list[Result]] = {}
    for r in rows:
        if r.discipline not in rows_per_discipline:
            rows_per_discipline[r.discipline] = []
        rows_per_discipline[r.discipline].append(r)

    OUTPUT_FOLDER.mkdir(exist_ok=True)

    for discipline, rows in rows_per_discipline.items():
        # Sort by total, and then by inner tens
        rows.sort(key=lambda r: (r.total, r.inner_tens), reverse=True)
        with open(OUTPUT_FOLDER / f'results-{date_str}-{discipline}.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(
                [
                    'Positie',
                    'Discipline',
                    '',
                    '',
                    'Licentienummer',
                    'Achternaam',
                    'Verenigingsnummer',
                    'Vereniging',
                    'S1',
                    'S2',
                    'S3',
                    'S4',
                    'S5',
                    'S6',
                    'M',
                    'Totaal'
                ]
            )

            for i, row in enumerate(rows):
                row = [
                    i+1,
                    row.discipline,
                    "",
                    "",
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
                ]
                writer.writerow(row)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "--date",
        type=lambda s: date.strptime(s, DATE_FORMAT),
        default=date.today(),
        help="The tournament date for which to fetch results."
    )
    args = argparser.parse_args()

    save_tournament_results_for_day(args.date)
