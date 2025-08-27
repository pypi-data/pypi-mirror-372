import logging
import os


def configure_logging() -> None:
    propagate_setting = os.getenv("URLLIB3_PROPAGATE", "False").lower() in [
        "true",
        "1",
        "t",
    ]
    logging.getLogger("urllib3").propagate = propagate_setting
