
import requests

def query_ten():
    url = 'http://127.0.0.1:47334/api/sql/query'
     # query
    resp = requests.post(url, json={'query':
                        'SHOW DATABASES;'})

    return resp.json()


def create_database():
    url = 'http://127.0.0.1:47334/api/sql/query'
    # query
    resp = requests.post(url, json={'query':
                        'CREATE DATABASE IF NOT EXISTS sync_mind WITH ENGINE = mongodb, PARAMETERS = {"key": "value"};'})
    
    return resp.json()

def show_handlers():
    url = 'http://127.0.0.1:47334/api/sql/query'
    # query
    resp = requests.post(url, json={'query':
                        'SHOW HANDLERS;'})

    return resp.json()