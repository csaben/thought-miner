import textwrap
from pathlib import Path


def reflow_text_from_file(input_file: Path, chunk_size: int = 55) -> None:
    with Path.open(input_file, "r") as f:
        text = f.read()
        # in case previously textwrapped, collapse to one line
        text = text.join("\n")

    # Use textwrap to efficiently split the text
    reflowed_text = textwrap.fill(text, width=chunk_size)

    with Path.open(input_file, "w") as f:
        f.write(reflowed_text)


def reflow_text_to_file(output_file: Path, text: str, chunk_size: int = 55) -> None:
    # in case previously textwrapped, collapse to one line
    text = text.join("\n")
    # Use textwrap to efficiently split the text
    reflowed_text = textwrap.fill(text, width=chunk_size)

    with Path.open(output_file, "w") as f:
        f.write(reflowed_text)


def reflow_text(text: str, chunk_size: int = 55) -> str:
    # in case previously textwrapped, collapse to one line
    text = "\n".join(text.splitlines())
    # Use textwrap to efficiently split the text
    return textwrap.fill(text, width=chunk_size)
