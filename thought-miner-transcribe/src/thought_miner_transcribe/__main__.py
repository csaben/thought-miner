import logging
from pathlib import Path

import click

from thought_miner_transcribe import __version__
from thought_miner_transcribe.api import _transcribe_folder_contents
from thought_miner_transcribe.app import run_server

LOGGER = logging.getLogger(__name__)


@click.group(help="thought-miner-transcribe CLI Application")
@click.version_option(version=__version__)
def thought_miner_transcribe() -> None:
    pass


@thought_miner_transcribe.command(name="start-server", help="Start the server")
def start_server() -> None:
    run_server()


@thought_miner_transcribe.command(
    name="transcribe-folder-contents", help="Echos a message"
)
@click.option(
    "--input-dir",
    help="Input dir of audio files",
)
@click.option(
    "--output-dir",
    type=click.Path(),
    help="Output directory for transcribed audio files",
)
def transcribe_folder_contents(input_dir: Path, output_dir: Path) -> None:
    _transcribe_folder_contents(input_dir=input_dir, output_dir=output_dir)


if __name__ == "__main__":
    thought_miner_transcribe(prog_name="thought-miner-transcribe")
