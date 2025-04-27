import os
from dotenv import load_dotenv
import requests
load_dotenv()

def connect_to_mindsdb():
    mindsdb_url = os.getenv('MINDSDB_URL', 'http://127.0.0.1:47334/api')
    print(f"Using MindsDB URL: {mindsdb_url}")
    return mindsdb_url

def list_datasources(base_url):
    try:
        url = f"{base_url}/databases"
        response = requests.get(url)
        response.raise_for_status()  
        return response.json()
    except Exception as e:
        print(f"Error fetching datasources: {str(e)}")
        return None
    