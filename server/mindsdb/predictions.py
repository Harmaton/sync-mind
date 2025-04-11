import requests
import os

def connect_to_mindsdb():
    """Get the MindsDB URL from environment variables or default to localhost."""
    mindsdb_host = os.getenv('MINDSDB_HOST', '127.0.0.1')
    mindsdb_port = os.getenv('MINDSDB_PORT', '47334')
    mindsdb_url = f"http://{mindsdb_host}:{mindsdb_port}"
    print(f"Using MindsDB URL: {mindsdb_url}")
    return mindsdb_url

def get_prediction(project_name: str, model_name: str, data: list[dict]) -> dict:
    """
    Get a single prediction from a specified MindsDB model.

    Args:
        project_name (str): The name of the project where the model resides.
        model_name (str): The name of the model to query.
        data (list[dict]): A list of dictionaries containing the input data for prediction.

    Returns:
        dict: The response from the API containing the prediction result.

    Raises:
        requests.exceptions.RequestException: If the API request fails.
    """
    base_url = connect_to_mindsdb()
    url = f"{base_url}/api/projects/{project_name}/models/{model_name}/predict"

    payload = data  # As per the API, the body is a list of objects (e.g., [{"sqft": "823", ...}])
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for 4xx/5xx status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting prediction: {str(e)}")
        if 'response' in locals():
            print(f"Response: {response.text}")
        raise

# # Example usage
# if __name__ == "__main__":
#     try:
#         prediction_data = [
#             {
#                 "sqft": "823",
#                 "location": "good",
#                 "neighborhood": "downtown",
#                 "days_on_market": "10"
#             }
#         ]
#         prediction_response = get_prediction(
#             project_name="mindsdb",
#             model_name="home_rentals_model",
#             data=prediction_data
#         )
#         print("Prediction result:", prediction_response)
#     except Exception as e:
#         print(f"Failed to get prediction: {e}")