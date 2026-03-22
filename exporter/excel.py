from typing import Any

from openpyxl.worksheet.worksheet import Worksheet

from models import Result


def insert_row_into_worksheet(
    worksheet: Worksheet,
    row: int,
    values: tuple[Any],
) -> None:
    """
    Inserts a group of values into the given row in the given Excel worksheet

    Args:
        worksheet (Worksheet): The Excel worksheet into which to insert the values
        row (int): The row number into which to insert the values
        values (tuple[Any]): The values to insert into the given row in the given Excel worksheet
    """

    for i, val in enumerate(values):
        col = chr(ord('@')+i+1)
        cell = f"{col}{row}"
        worksheet[cell] = val


def add_results_to_worksheet(
    results_per_discipline: dict[str, list[Result]],
    worksheet: Worksheet,
    starting_row: int,
) -> None:
    """
    Inserts the given results (grouped by discipline) into the given Excel worksheet.
    Inserted results are grouped by discipline and sorted by total score and inner tens
    within each group

    Args:
        results_per_discipline (dict[str, list[Result]]): Dictionary mapping discipline names
            to lists of Result objects representing the competition results to insert into the
            given Excel worksheet
        worksheet (Worksheet): The Excel worksheet into which to insert the results
        starting_row (int): The row number in the Excel worksheet at which to start inserting
            the results
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
