"""
airbyte package for managing the data pipeline.
"""

from .pipeline import run_sync, list_sources, list_destinations, generate_token
from .destination import setup_mongo_db_destination
from .orchestrator import setup_airbyte_connections

__all__ = [
    'run_sync',
    'list_sources',
    'list_destinations',
    'generate_token',
    'setup_mongo_db_destination',
    'setup_airbyte_connections'
]