from fastapi import HTTPException

def setup_shopify_source(config: dict) -> dict:
    """
    Setup the Shopify source with the given configuration.
    """
    try:
        return setup_shopify_source(config)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

def setup_postgress_destination():
    return {"Postgres destination configured successfully"}