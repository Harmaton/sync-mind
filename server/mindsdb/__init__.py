"""
minds_db package for managing Mindsdb datasources and minds.
"""

from .connect import connect_to_mindsdb, list_datasources
from .retiever import gemini_retrieve_answer, shopify_text2sql_answer
from .slack_storage import store_slack_message, store_slack_thread_message
from .minds_setup import mindsdb_setup

__all__ = [
    'connect_to_mindsdb',
    'list_datasources',
    'gemini_retrieve_answer',
    'shopify_text2sql_answer',
    'store_slack_message',
    'store_slack_thread_message',
    'mindsdb_setup'
]