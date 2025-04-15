import os
import requests
from fastapi import HTTPException
from models import MongoDBConfig
from .pipeline import generate_token

url = "https://api.airbyte.com/v1/destinations"


def setup_mongo_db_destination(config: MongoDBConfig) -> dict:
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
        # Generate access token for Airbyte API
        token_response = generate_token()
        access_token = token_response.get("access_token")

        # Construct the payload with hardcoded and dynamic values
        payload = {
            "name": "MongoDB-Destination",  # Hardcoded as specified
            "workspaceId": config.workspaceId,
            "configuration": {
                "destinationType": "mongodb",  # Hardcoded as specified
                "instance_type": {
                    "instance": "atlas",
                    "cluster_url": config.cluster_url,
                },
                "database": config.database,
                "auth_type": {
                    "authorization": "login/password",
                    "username": config.username,
                    "password": config.password,
                },
            },
        }

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }

        # Make the API request to create the destination
        response = requests.post(url, json=payload, headers=headers)

        # Check for unsuccessful response status
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        print(response.text)
        
        return {"message": "MongoDB destination configured successfully"}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect to Airbyte API: {str(e)}")

