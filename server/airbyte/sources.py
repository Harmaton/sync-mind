from fastapi import HTTPException
import requests
from settings import Settings

url = "https://api.airbyte.com/v1/sources"

settings = Settings()

def setup_SPX_polygon_source():
    try:
        payload = {
            "name": "SPX_Polygon-source",  
            "workspaceId": settings.airbyte_workspace_id,
            "configuration": {
                "apiKey": settings.polygon_api_key,
                "start_date": settings.polygon_start_date,
                "sourceType": "polygon-stock-api",
                "stocksTicker": "US500",
                "timespan": "4h"
            }
        }

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        print(response.text)
        return {"message":"Setting up polygon data source"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))