"""
airbyte package for managing the data pipeline.
"""

from .pipeline import run_sync, list_sources, list_destinations, generate_token
from .destinations import setup_mongo_db_destination

__all__ = [
    'run_sync',
    'list_sources',
    'list_destinations',
    'generate_token',
    'setup_mongo_db_destination'
]