# Meyton Results To KNSA Spreadsheet Exporter

This repository contains an utility script to export competition results from Meyton's electronic shooting range system database into excel workbooks that follow a standardised format provided by the KNSA (Royal Dutch Shooting Association).

The script takes a base Excel file as input and fills it out with the series results for the given date queried from a Meyton database. The output file will carry the name of the original Excel file with the given date as extra suffix.

## Environment setup

### Python and packages

First install Python 3.14 (might work with lower versions but untested). After this the necessary Python packages can be installed using pip by running the following command in the repository root:
```sh
pip install -r requirements.txt
```

### Environment variables

In order to run the script several environment variables need to be set to configure the correct MariaDB credentials and connection information. The following environment variables are configurable (and most are expected):

| Environment variable | Default | Description                                                                |
| -------------------- | --------| -------------------------------------------------------------------------- |
| MARIADB_USER         |         | The user to use for authentication to the MariaDB server                   |
| MARIADB_PASSWORD     |         | The password to use for authentication to the MariaDB server               |
| MARIADB_HOST         |         | The IP address at which the MariaDB endpoint is located                    |
| MARIADB_PORT         | 3306    | The port number through which the MariaDB endpoint can be accessed         |
| MARIADB_DATABASE     |         | The name of the database in the MariaDB server that should be connected to |

For local execution, all of these environment variables can be set in a `.env` file in the root of the repository. The `.env` file should have the following format:

```
MARIADB_USER=
MARIADB_PASSWORD=
MARIADB_HOST=
MARIADB_PORT=
MARIADB_DATABASE=
```

## Script execution

The script can be executed using the following command from the repository root:
```sh
python exporter/main.py
```

A number of command line parameters are available for customizing the behaviour of the script. They're as follows:

| Command line parameter | Default                        | Description                                                                                 |
| ---------------------- | ------------------------------ | ------------------------------------------------------------------------------------------- |
| base-xls-file          | input/Rankinglijst.xlsm        | The path (from the repository root) to the Excel workbook/file to use as base               |
| xls-worksheet          | Resultaten                     | The name of the worksheet to use in the Excel workbook/file                                 |
| xls-date-cell          | E5                             | The cell to write the competition date to (Excel cell identifier format)                    |
| xls-content-start-row  | 9                              | The starting row from which all results should be inserted (Excel row number)               |
| date                   | *Today*                        | The competition date for which results should be collected and exported (format YYYY-MM-DD) |
| output-folder          | output                         | The output folder to which the completed Excel file should be saved                         |

All of these parameters can be included as standard CLI parameters. For example:
```sh
python exporter/main.py --base-xls-file input/ranking-list.xlsm --xls-worksheet Results --xls-date-cell E5 --xls-content-start-row 9 --date 2026-03-21 --output-folder output
```
