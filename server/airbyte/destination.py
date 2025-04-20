import os
import requests
from fastapi import HTTPException
from models import MongoDBConfig
from settings import Settings
from .pipeline import generate_token

url = "https://api.airbyte.com/v1/destinations"
settings = Settings()
def setup_mongo_db_destination() -> dict:
    """
    Setup the MongoDB destination with the given configuration.
    
    Args:
        config (MongoDBConfig): Configuration for MongoDB destination, validated by Pydantic.
    
    Returns:
        dict: Success message if the destination is configured.
    
    Raises:
        HTTPException: If the configuration fails or the API request encounters an error.
    """
    try:
        token_response = generate_token()
        access_token = token_response.get("access_token")

        payload = {
            "name": "MongoDB-Destination",  
            "workspaceId": settings.airbyte_workspace_id,
            "configuration": {
                "destinationType": "mongodb", 
                "instance_type": {
                    "instance": "atlas",
                    "cluster_url": settings.mongo_cluster_url,
                },
                "database": settings.mongo_database,
                "auth_type": {
                    "authorization": "login/password",
                    "username": settings.mongo_username,
                    "password": settings.mongo_password
                },
            },
        }

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        print(response.text)
        
        return {"message": "MongoDB destination configured successfully"}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect to Airbyte API: {str(e)}")

