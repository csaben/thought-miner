import textwrap
from pathlib import Path

import nltk
from nltk.tokenize import sent_tokenize

# Download the Punkt tokenizer models (only needed once)
nltk.download("punkt")


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
    """Reflows the given text into chunks of the specified size.

    Args:
        text (str): The input text to reflow.
        chunk_size (int): The maximum width of each line.

    Returns:
        str: The reflowed text.
    """
    # Collapse any existing newlines into spaces
    text = " ".join(text.splitlines())

    # Use textwrap to reflow the text into chunks
    reflowed_text = textwrap.fill(text, width=chunk_size)

    # Ensure the output ends with a newline
    return reflowed_text


# having some attempts at sentence based reflow
def reflow_text_with_sentences(text: str, chunk_size: int = 55) -> str:
    # Split into sentences
    sentences = sent_tokenize(text)

    # Reflow each sentence individually
    reflowed_text = []
    for sentence in sentences:
        # Collapse to one line within the sentence
        sent = " ".join(sentence.splitlines())
        # Reflow the sentence
        reflowed_sentence = textwrap.fill(sent, width=chunk_size)
        reflowed_text.append(reflowed_sentence)

    # Join sentences with newlines
    return "\n".join(reflowed_text)
