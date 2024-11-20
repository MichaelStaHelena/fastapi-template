import logging
from pathlib import Path
from typing import Any, Dict


def setup_logging(
        log_level: str = "INFO",
        log_file: str = "app.log",
        log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
) -> Dict[str, Any]:
    log_path = Path("logs")
    log_path.mkdir(exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, log_level),
        format=log_format,
        handlers=[
            logging.FileHandler(log_path / log_file),
            logging.StreamHandler()
        ]
    )

    return {"log_level": log_level, "log_file": str(log_path / log_file)}


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(f"app.{name}")
