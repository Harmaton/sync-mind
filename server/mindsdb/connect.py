
import os
from dotenv import load_dotenv
import requests
load_dotenv()

def connect_to_mindsdb():
    mindsdb_url = os.getenv('MINDSDB_URL', 'http://127.0.0.1:47334')
    print(f"Using MindsDB URL: {mindsdb_url}")
    return mindsdb_url

def list_datasources(base_url):
    try:
        url = f"{base_url}/databases"
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for error status codes
        return response.json()
    except Exception as e:
        print(f"Error fetching datasources: {str(e)}")
        return None
    
def create_postgres_datasource(base_url, datasource_name, host, port, username, password, database):
    try:
        url = f"{base_url}/api/databases/{datasource_name}"
        payload = {
            "engine": "postgres",
            "connection_data": {
                "host": host,
                "port": port,
                "user": username,
                "password": password,
                "database": database
            }
        }
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.post(url, json=payload, headers=headers)
        print(f"Response status code: {response.status_code}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error creating Postgres datasource: {str(e)}")
        return None