import logging
from .add_captions import add_captions
from importlib.metadata import version


def setup_logging(log_file=None):
    logger = logging.getLogger("shortcap")
    logger.setLevel(logging.INFO)

    # Remove polluting logs from PIL
    logging.getLogger("PIL").setLevel(logging.WARNING)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# Default setup (logs to console only)
logger = setup_logging()


# You can expose a function to allow users to configure logging
def configure_logging(log_file=None):
    global logger
    logger = setup_logging(log_file)


__version__ = version("shortcap")
__all__ = ["add_captions", "configure_logging"]
