
from mindsdb import connect_to_mindsdb
import requests

def create_agent(project_name: str, agent_name: str, model: str, skills: list[str]) -> dict:
    """
    Create an agent in a specified MindsDB project.

    Args:
        project_name (str): The name of the project where the agent resides.
        agent_name (str): The name of the agent to create.
        model (str): The conversational model used by the agent.
        skills (list[str]): A list of skills the agent can use.

    Returns:
        dict: The response from the API containing the created agent's details.

    Raises:
        requests.exceptions.RequestException: If the API request fails.
    """
    base_url = connect_to_mindsdb()
    url = f"{base_url}/api/projects/{project_name}/agents"
    
    payload = {
        "agent": {
            "name": agent_name,
            "model": model,
            "skills": skills
        }
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error creating agent: {str(e)}")
        if response is not None:
            print(f"Response: {response.text}")
        raise


def query_agent(project_name: str, agent_name: str, messages: list[dict]) -> dict:
    """
    Query an agent in a specified MindsDB project with a list of messages.

    Args:
        project_name (str): The name of the project where the agent resides.
        agent_name (str): The name of the agent to query.
        messages (list[dict]): A list of message objects with 'question' and 'answer' keys.

    Returns:
        dict: The response from the API containing the agent's message.

    Raises:
        requests.exceptions.RequestException: If the API request fails.
    """
    base_url = connect_to_mindsdb()
    url = f"{base_url}/api/projects/{project_name}/agents/{agent_name}/completions"
    
    payload = {
        "messages": messages
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for 4xx/5xx status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error querying agent: {str(e)}")
        if response is not None:
            print(f"Response: {response.text}")
        raise