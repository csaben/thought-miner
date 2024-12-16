import click
from thought_miner_alignment import __version__


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


if __name__ == "__main__":
    thought_miner_alignment(prog_name="thought-miner-alignment")
