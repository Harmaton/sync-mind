
import requests

def query_ten():
    url = 'http://127.0.0.1:47334/api/sql/query'
     # query
    resp = requests.post(url, json={'query':
                        'SHOW DATABASES;'})

    return resp.json()