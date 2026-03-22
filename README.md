# Meyton Results To KNSA Spreadsheet Exporter

This repository contains an utility script to export competition results from Meyton's electronic shooting range system database into excel workbooks that follow a standardised format provided by the KNSA (Royal Dutch Shooting Association).

The script takes a base Excel file as input and fills it out with the series results for the given date queried from a Meyton database. The output file will carry the name of the original Excel file with the given date as extra suffix.

By default the exporter script expects an `input` folder to exist in the current working directly. In this folder an Excel workbook/file `Rankinglijst.xlsm` should be located that can be used as base for creating the completed results workbook.

The base Excel workbook is expected to follow the KNSA template format and have a competition date cell at cell `E5` (which will have a competition date inserted into it). It is also expected to have empty rows (for new results) available starting at row `9`. Finally, the filled out Excel workbook is saved in an `output` folder in the current working directory and it will be created if it doesn't exist. All of the mentioned behaviour can be customized using CLI parameters.

## Configuration

The script has to have certain environment variables configured and can optionally be further configured using certain CLI parameters.

### Environment variables

In order to run the script several environment variables need to be set to configure the correct MariaDB credentials and connection information. The following environment variables are configurable (and most are assumed to be there):

| Environment variable | Default | Description                                                                |
| -------------------- | --------| -------------------------------------------------------------------------- |
| MARIADB_USER         |         | The user to use for authentication to the MariaDB server                   |
| MARIADB_PASSWORD     |         | The password to use for authentication to the MariaDB server               |
| MARIADB_HOST         |         | The IP address at which the MariaDB endpoint is located                    |
| MARIADB_PORT         | 3306    | The port number through which the MariaDB endpoint can be accessed         |
| MARIADB_DATABASE     |         | The name of the database in the MariaDB server that should be connected to |

### Command line interface parameters

The execution of the script can be optionally customized using the following CLI parameters:

| Command line parameter | Default                        | Description                                                                                 |
| ---------------------- | ------------------------------ | ------------------------------------------------------------------------------------------- |
| base-xls-file          | input/Rankinglijst.xlsm        | The path (from the repository root) to the Excel workbook/file to use as base               |
| xls-worksheet          | Resultaten                     | The name of the worksheet to use in the Excel workbook/file                                 |
| xls-date-cell          | E5                             | The cell to write the competition date to (Excel cell identifier format)                    |
| xls-content-start-row  | 9                              | The starting row from which all results should be inserted (Excel row number)               |
| date                   | *Today*                        | The competition date for which results should be collected and exported (format YYYY-MM-DD) |
| output-folder          | output                         | The output folder to which the completed Excel file should be saved                         |


## Local environment execution

It's possible to run the script locally provided you have direct access to the MariaDB endpoint.

### Preparation

First install Python 3.14 (might work with lower versions but untested). Optionally set up a virtual environment. After this the necessary Python packages can be installed using pip by running the following command in the repository root:
```sh
pip install -r requirements.txt
```

All of the necessary environment variables can be set in a `.env` file in the root of the repository. The `.env` file should have the following format:

```
MARIADB_USER=
MARIADB_PASSWORD=
MARIADB_HOST=
MARIADB_PORT=
MARIADB_DATABASE=
```

### Execution

The script can be executed using the following command from the repository root:
```sh
python exporter/main.py
```

The above mentioned CLI parameters can also be added to customize the script behaviour. For example:
```sh
python exporter/main.py --base-xls-file input/ranking-list.xlsm --xls-worksheet Results --xls-date-cell E5 --xls-content-start-row 9 --date 2026-03-21 --output-folder output
```

## Docker image execution

The script can also be run in a Docker container. This has the benefit of using a self-contained environment that's easily reproducable in a cross-platform way

### Preparation

First install Docker. After this you can build the Docker image using the following command in the repository root:
```sh
docker build -t meyton-to-knsa-exporter:<tag> .
```

Also create a `docker.env` file that will contain environment variable values with the required MariaDB configuration (see earlier section for an example). You can skip this if you want to pass the environment variables separately using the `--env` CLI parameter for the `docker run` command.

If you're running this script from the repository root you can use the provided input KNSA Excel workbook template or add your own template to the `input` folder.
Make sure you add an `output` folder to which the completed Excel workbooks can be written.

It's also possible to run the Docker container from anywhere on your machine, but you have to make sure subdirectories for input and output are available

### Execution

The Docker container (based on the built image) can be run using the following command, if run from the repository root (with created `output` folder and `docker.env` environment variables file):
```sh
docker run --env-file docker.env --volume $(pwd)/input:/home/appuser/app/input --volume $(pwd)/output:/home/appuser/app/output meyton-to-knsa-exporter:local
```

This will mount the `input` and `output` subdirectories in the Docker container and run the script, such that the output Excel workbook will appear in the `output` directory.

It's also possible to pass CLI parameters to the script by appending them to the `docker run` invocation. For example:
```sh
docker run --env-file docker.env --volume $(pwd)/input:/home/appuser/app/input --volume $(pwd)/output:/home/appuser/app/output meyton-to-knsa-exporter:local --date 2026-01-31
```

Like mentioned earlier it's also possible to use `--env` flags instead of `--env-file` with a environment variable file. And it's possible to run the container anywhere on the system so long as the image was built. Adjust the volume mounts accordingly if you do that.

