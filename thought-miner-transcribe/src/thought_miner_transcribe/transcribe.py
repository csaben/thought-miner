import logging
from pathlib import Path

import whisper

LOGGER = logging.getLogger(__name__)
model = whisper.load_model("base")
CHUNK_LIM = 480000


def transcribe_with_chunking(path: Path) -> str:
    audios = []
    audio = whisper.load_audio(path)

    # if smaller than 30 sec, move on
    if len(audio) <= CHUNK_LIM:
        audio = whisper.pad_or_trim(audio)
        audios.append(audio)

    # if larger than 30 sec, chunk it and pad last piece
    else:

        for i in range(0, len(audio), CHUNK_LIM):
            chunk = audio[i : i + CHUNK_LIM]
            chunk_index = len(chunk)
            if chunk_index < CHUNK_LIM:
                chunk = whisper.pad_or_trim(chunk)
            audios.append(chunk)

    results = ""

    for chunk in audios:
        LOGGER.info(chunk.shape)
        # chunk = whisper.pad_or_trim(chunk)
        # make log-Mel spectrogram and move to the same device as the model
        mel = whisper.log_mel_spectrogram(chunk).to(model.device)

        # decode the audio
        options = whisper.DecodingOptions(fp16=False)
        result = whisper.decode(model, mel, options)
        LOGGER.info(result)
        results += result.text

    return results


def transcribe(path: Path) -> str:
    # # load audio and pad/trim it to fit 30 seconds
    audio = whisper.load_audio(path)
    audio = whisper.pad_or_trim(audio)
    LOGGER.info(audio.shape)

    # # make log-Mel spectrogram and move to the same device as the model
    mel = whisper.log_mel_spectrogram(audio).to(model.device)

    # # detect the spoken language
    _, probs = model.detect_language(mel)
    LOGGER.info(f"Detected language: {max(probs, key=probs.get)}")  # noqa: G004

    # # decode the audio
    options = whisper.DecodingOptions(fp16=False)
    result = whisper.decode(model, mel, options)

    # # LOGGER.info the recognized text
    return result.text
