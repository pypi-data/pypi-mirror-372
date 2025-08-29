"""
RD Station API Helper
"""
import logging
from typing import Optional

from .client import RDStationAPI
from .dataclasses import (
    Segmentation,
    SegmentationContact,
    Contact,
    ContactFunnelStatus,
    ConversionEvents,
    Lead,
)
from .exceptions import (
    APIError,
    AuthenticationError,
    ConfigurationError,
    DataProcessingError,
    ValidationError,
)
from .utils import PostgresDB, PgConfig

# Main exports
__all__ = [
    "RDStationAPI",
    # Utils
    "PostgresDB",
    "PgConfig",
    # Exceptions
    "AuthenticationError",
    "ValidationError",
    "APIError",
    "DataProcessingError",
    "ConfigurationError",
    # Dataclasses
    "Segmentation",
    "SegmentationContact",
    "Contact",
    "ContactFunnelStatus",
    "ConversionEvents",
    "Lead",
    # __init__
    "setup_logging",
]


def setup_logging(level: int = logging.INFO,
                  format_string: Optional[str] = None) -> None:
    """
    Setup logging configuration.

    Args:
        level (int): Logging level (default: INFO)
        format_string (Optional[str]): Custom format string
    """
    if format_string is None:
        format_string = '%(levelname)s - %(message)s'

    logging.basicConfig(
        level=level,
        format=format_string,
        handlers=[
            logging.StreamHandler(),
        ]
    )
