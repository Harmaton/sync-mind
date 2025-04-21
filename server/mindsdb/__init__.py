"""
minds_db package for managing Mindsdb datasources and minds.
"""

from .mind import create_mind, query_mind
from .connect import connect_to_mindsdb, create_postgres_datasource, list_datasources
from .projects import query_ten, show_handlers

__all__ = [
    'create_mind',
    'query_mind',
    'connect_to_mindsdb',
    'create_postgres_datasource'
    'list_datasources'
    'query_ten',
    'show_handlers'
]