from pathlib import Path

import click
from thought_miner_alignment import __version__
from thought_miner_alignment.align import process_pair
from thought_miner_alignment.app import run_server


@click.group(help="thought-miner-alignment CLI Application")
@click.version_option(version=__version__)
def thought_miner_alignment() -> None:
    pass


@thought_miner_alignment.command(name="echo", help="Echos a message")
@click.argument("message", type=str)
@click.option(
    "-s/-n",
    "--shout/--no-shout",
    default=False,
    help="whether to shout the message  [default no shout]",
    show_default=False,
)
@click.option(
    "-r",
    "--repeat",
    default=1,
    help="how many times to repeat the message",
    show_default=True,
)
def echo(message: str, shout: bool = False, repeat: int = 1) -> None:
    if shout:
        message = message.upper()
    for _ in range(repeat):
        print(message)


@thought_miner_alignment.command(name="align", help="aligns a pair")
@click.argument("audio_path", type=click.Path())
@click.argument("text_path", type=click.Path())
def align(audio_path: Path, text_path: Path) -> None:
    map = process_pair(audio_path=audio_path, text_path=text_path)
    print(map)


@thought_miner_alignment.command(name="start-server", help="Start the server")
def start_server() -> None:
    run_server()


"""
thought-miner-alignment align "/home/arelius/workspace/thought.fzf/data/audio/world model at last.m4a" "/home/arelius/workspace/thought.fzf/data/transcriptions/default/world model at last.txt"
"""
if __name__ == "__main__":
    thought_miner_alignment(prog_name="thought-miner-alignment")
