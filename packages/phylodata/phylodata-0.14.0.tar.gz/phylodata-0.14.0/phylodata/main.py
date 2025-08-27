import subprocess
from pathlib import Path

import click

import phylodata
from phylodata.data_types import get_schema, validate_editable_json


@click.group()
def cli(): ...


@cli.command(help="Process an experiment before uploading it to PhyloData.")
def process():
    subprocess.run(
        ["streamlit", "run", str(Path(phylodata.__path__[0]) / "process/ui.py")]
    )  # type: ignore


@cli.command(
    help="Validate if a given JSON file contains valid editable PhyloData metadata."
)
@click.argument("file_path", type=click.Path(exists=True))
def validate(file_path: str):
    validate_editable_json(file_path)
    print("File is valid!")


@cli.command(help="Prints the JSON schema for valid PhyloData editable metadata files.")
def schema():
    print(get_schema())
