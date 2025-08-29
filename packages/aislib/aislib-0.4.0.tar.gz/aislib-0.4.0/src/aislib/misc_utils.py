import copy
import logging
from pathlib import Path

from termcolor import colored
from tqdm import tqdm


class TQDMLoggingHandler(logging.Handler):
    def __init__(self, level=logging.NOTSET):
        super().__init__(level)

    def emit(self, record):
        try:
            msg = self.format(record)
            tqdm.write(msg)
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)


class ColoredFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: "blue",
        logging.INFO: "green",
        logging.WARNING: "yellow",
        logging.ERROR: "red",
    }

    def format(self, record):
        record_copy = copy.copy(record)
        levelname_color = self.COLORS.get(record_copy.levelno)
        if levelname_color:
            record_copy.levelname = colored(record_copy.levelname, levelname_color)
        return super().format(record_copy)


def get_logger(name: str, tqdm_compatible: bool = False) -> logging.Logger:
    """
    Creates a logger with a debug level and a custom format.

    :param name: Name to give logger.
    :param tqdm_compatible: Overwrite default stream.write in favor of tqdm.write
    to avoid breaking progress bar.
    :return: Logger object.
    """
    logger_ = logging.getLogger(name)
    logger_.handlers.clear()
    logger_.propagate = False
    logger_.setLevel(logging.DEBUG)

    handler = TQDMLoggingHandler() if tqdm_compatible else logging.StreamHandler()

    formatter = ColoredFormatter(
        fmt="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger_.addHandler(handler)
    return logger_


def ensure_path_exists(path: Path, is_folder: bool = False) -> Path:
    """
    Small utility function to ensure a path exists before trying to save a file.

    :param path: Path to make directories for.
    :param is_folder: Whether the output is a folder or not, if not we just
    create the parent folder.
    :return: The generated path the function just created.
    """
    if not is_folder:
        path = Path("/".join(path.parts[:-1]))

    path.mkdir(parents=True, exist_ok=True)

    return path
