import logging
from config import REPO_ROOT


def setup_logging(verbose=False):
    log_path = REPO_ROOT / "diagnostics.log"

    console_level = (
        logging.INFO
        if verbose
        else logging.WARNING
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)

    file_handler = logging.FileHandler(
        log_path,
        mode="w"
    )
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s | "
        "%(levelname)-8s | "
        "%(name)s | "
        "%(message)s"
    )

    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[
            console_handler,
            file_handler
        ]
    )