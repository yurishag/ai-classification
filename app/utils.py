"""
app/utils.py

Contains the utility functions used by the microservice:
1. logging
"""

import logging

def setup_logging():
    logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

logger = logging.getLogger(__name__)