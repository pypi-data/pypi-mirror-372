r"""
# Welcome to the API documentation of AI-Link Version 3.1.0

Here you will find the full documentation of all publicly facing functions of AI-Link.
"""

import logging

logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.WARNING,
)

__all__ = ["base", "client", "data_model", "db", "repo", "catalog"]
