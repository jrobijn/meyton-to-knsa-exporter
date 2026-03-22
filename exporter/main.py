import argparse
import os
from datetime import date
from models import DatabaseSettings
from pathlib import Path

import openpyxl
from dotenv import load_dotenv

from db import get_results_per_discipline
from excel import add_results_to_worksheet

load_dotenv()


def main(
    db_settings: DatabaseSettings,
    day: date,
    base_xls_file: Path,
    xls_worksheet: str,
    xls_date_cell: str,
    xls_content_start_row: int,
    output_folder: Path,
):
    """
    Main function of the Meyton results exporter. Fetches the competition results for the
    given day from the Meyton database, and exports them to an Excel file based on the given
    base Excel file.

    Args:
        db_settings (DatabaseSettings): Object containing the database connection configuration
        day (date): The tournament date for which to fetch results
        base_xls_file (Path): Path to the base Excel file
        xls_worksheet (str): Name of the worksheet in the Excel file
        xls_date_cell (str): Cell in the Excel worksheet where the tournament date should be
            inserted
        xls_content_start_row (int): Row number in the Excel worksheet at which to
            start inserting the results
        output_folder (Path): Path to the folder where the updated Excel file should be saved
    """

    results_per_discipline = get_results_per_discipline(db_settings, day)

    # Load Excel worksheet that's used as a base
    workbook = openpyxl.load_workbook(base_xls_file)
    worksheet = workbook[xls_worksheet]

    # Update dynamic worksheet metadata
    worksheet[xls_date_cell] = f"{day.month}/{day.day}/{day.year}"
    # Add results to Excel worksheet
    add_results_to_worksheet(results_per_discipline, worksheet, xls_content_start_row)

    # Store the updated Excel workbook in the output folder
    output_folder.mkdir(exist_ok=True)
    date_str = day.strftime("%Y-%m-%d")
    workbook.save(output_folder / f'{base_xls_file.stem}-{date_str}.xlsx')
    

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "--base-xls-file",
        type=Path,
        default=Path("input") / "Rankinglijst.xlsm"
    )
    argparser.add_argument(
        "--xls-worksheet",
        type=str,
        default="Resultaten"
    )
    argparser.add_argument(
        "--xls-date-cell",
        type=str,
        default="E5"
    )
    argparser.add_argument(
        "--xls-content-start-row",
        type=int,
        default=9
    )
    argparser.add_argument(
        "--date",
        type=lambda s: date.strptime(s, "%Y-%m-%d"),
        default=date.today(),
        help="The tournament date for which to fetch results."
    )
    argparser.add_argument(
        "--output-folder",
        type=Path,
        default=Path("output")
    )
    args = argparser.parse_args()

    db_settings = DatabaseSettings(
        user=os.getenv("MARIADB_USER"),
        password=os.getenv("MARIADB_PASSWORD"),
        host=os.getenv("MARIADB_HOST"),
        port=int(os.getenv("MARIADB_PORT", "3306")),
        database=os.getenv("MARIADB_DATABASE")
    )

    main(
        db_settings=db_settings,
        base_xls_file=args.base_xls_file,
        xls_worksheet=args.xls_worksheet,
        xls_date_cell=args.xls_date_cell,
        xls_content_start_row=args.xls_content_start_row,
        day=args.date,
        output_folder=args.output_folder,
    )
