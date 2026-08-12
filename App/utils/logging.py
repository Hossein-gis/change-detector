# ============================================================
# Project:      OpenCD Change Detection
# Version:      v1.0
# Created:      2026-07-10
# Purpose:      Structured logging setup
# Last Updated: 2026-07-10
# ============================================================

import logging
import sys
from pathlib import Path


def setup_logger(
    log_file="logs/inference.log",
    level="INFO",
    verbose=False,
):
    """Configure and return a logger instance."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    logger = logging.getLogger("opencd")
    logger.setLevel(numeric_level)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(numeric_level if verbose else logging.INFO)
    console.setFormatter(formatter)
    logger.addHandler(console)

    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_path, mode="a")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
