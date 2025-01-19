import logging

LOGGER: logging.Logger = logging.getLogger(__name__)


def setup_logger(log_level: str) -> None:
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        msg = f"Invalid log level: {log_level}"
        raise ValueError(msg)  # noqa: TRY004
    LOGGER.setLevel(numeric_level)

    # Create console handler and set level
    ch = logging.StreamHandler()
    ch.setLevel(numeric_level)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Add formatter to ch
    ch.setFormatter(formatter)

    # Add ch to logger
    LOGGER.addHandler(ch)
