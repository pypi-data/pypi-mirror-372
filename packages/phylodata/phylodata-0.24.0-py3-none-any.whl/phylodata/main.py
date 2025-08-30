import subprocess
from pathlib import Path

import click

import phylodata
from phylodata.data_types import get_schema, validate_editable_json
from phylodata.process.correct_language import correct_language


@click.group()
def cli(): ...


@cli.command(help="Process an experiment before uploading it to PhyloData.")
@click.argument("files", nargs=-1, type=click.UNPROCESSED)
def process(files):
    subprocess.run(
        ["streamlit", "run", str(Path(phylodata.__path__[0]) / "process/ui.py"), *files]
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


@cli.command(help="Corrects the language of a sample in a metadata file.")
@click.argument("metadata_file", type=click.Path(exists=True))
@click.argument("sample_id", type=str)
@click.argument("language_label", type=str)
def change_language(metadata_file: str, sample_id: str, language_label: str):
    correct_language(Path(metadata_file), sample_id, language_label)
