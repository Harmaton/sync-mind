import requests

from server.settings import Settings

url = "http://127.0.0.1:47334/api/databases"

settings = Settings()

def connect_datasource():
    """
    Connect to the data source.
    """
  
    payload = {
        "database": {
        "name": "mongo_datasource",
        "engine": "mongo",
        "parameters": {
        "host":settings.mindsdb_url,                         
        "port": " ",                           
        "user": settings.mongo_username,                           
        "password":settings.mongo_password,                    
        "database": settings.mongo_database 
        }}
    }

    headers = {"Content-Type": "application/json"}

    response = requests.request("POST", url, json=payload, headers=headers)

    print(response.text)
