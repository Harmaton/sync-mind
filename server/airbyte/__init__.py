"""
airbyte package for managing the data pipeline.
"""

from .pipeline import run_syncs, list_sources, list_destinations, config_source_coinapi, config_destination_mduck, generate_token

__all__ = [
    'run_syncs',
    'list_sources',
    'list_destinations',
    'config_source_coinapi',
    'config_destination_mduck',
    'generate_token'
]