import logging
from urllib.parse import urlparse

import okapi_aether_sdk


def split_url_parts(full_url: str) -> tuple[str, str]:
    """
    Split a full URL into (base_url, endpoint_path).
    """
    parsed = urlparse(full_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    endpoint_path = parsed.path.lstrip("/")
    return base_url, endpoint_path


def get_default_logger() -> logging.Logger:
    """Get the default logger configuration.

    Configure a default logger. Default logger will have be a
    StreamHandler of INFO level with a pre-defined format.

    :return logging.Logger: Configured logger.
    """
    logger = logging.getLogger(okapi_aether_sdk.__name__)
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)8s] %(message)s")
    handler.setFormatter(formatter)

    # Avoid adding multiple handlers if this code runs more than once
    logger.handlers = [h for h in logger.handlers if not isinstance(h, logging.NullHandler)]
    if not logger.hasHandlers():
        logger.addHandler(handler)

    return logger
