import logging
import os
from pathlib import Path

from thought_miner_transcribe.core import transcribe_with_chunking

LOGGER = logging.getLogger(__name__)


def _transcribe_folder_contents(input_dir: Path, output_dir: Path) -> None:
    Path.makedirs(output_dir, exist_ok=True)
    files = os.listdir(input_dir)

    for file in files:
        text = transcribe_with_chunking(Path(input_dir) / file)
        file_name = output_dir / Path(f"{Path(file).stem}.txt")
        print(file_name)
        print(Path(file).stem)
        with Path.open(file_name, "w") as f:
            f.write(text)
            LOGGER.info("Text data written to %s", file_name)

    LOGGER.info("Finished transcribing from %s", input_dir)
