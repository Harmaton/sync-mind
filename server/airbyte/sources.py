from fastapi import HTTPException
import requests
from settings import Settings
from .pipeline import generate_token

url = "https://api.airbyte.com/v1/sources"

settings = Settings()

def setup_shopify_source(config: dict) -> dict:
    """
    Setup the Shopify source with the given configuration.
    """
    try:
        token_response = generate_token()
        access_token = token_response.get("access_token")

        payload = {
            "name": "Shopify-source",  
            "workspaceId": settings.airbyte_workspace_id,
            "configuration": {
               "shop": "",
               "credentials": {
                "auth_method": "api_password",
               "api_password": settings.shopify_api_password 
               },
               "sourceType": "shopify"
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
        return {"message":"Setting up shopify data source"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
