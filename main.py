import mariadb
import openpyxl
from dotenv import load_dotenv

import argparse
import csv
import os
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

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
    rows: list[tuple] = cur.fetchall()

    rows_per_discipline: dict[str, list[tuple]] = {}
    for row in rows:
        discipline = row[9]
        if discipline not in rows_per_discipline:
            rows_per_discipline[discipline] = []
        rows_per_discipline[discipline].append(row)

    OUTPUT_FOLDER.mkdir(exist_ok=True)

    for discipline, rows in rows_per_discipline.items():
        # Sort by total, and then by inner tens
        rows.sort(key=lambda x: (x[15], x[14]), reverse=True)
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

            for i, (
                sport_pass_id,
                first_name,
                last_name,
                club,
                club_id,
                starter_list,
                starter_list_id,
                start_number,
                target_number,
                discipline,
                ranking,
                series1,
                series2,
                series3,
                inner_tens,
                total
            ) in enumerate(rows):
                name = f"{last_name} - {first_name}"
                row = [
                    i+1,
                    discipline,
                    "",
                    "",
                    sport_pass_id,
                    name,
                    club_id,
                    club,
                    series1,
                    series2,
                    series3,
                    "",
                    "",
                    "",
                    inner_tens,
                    round(total/10)
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
