import logging
import os

logger = logging.getLogger("Anzar")


if os.getenv("ENV") == "dev":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(asctime)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )
else:
    logger.addHandler(logging.NullHandler())
