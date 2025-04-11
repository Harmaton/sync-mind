import requests
import os

def connect_to_mindsdb():
    """Get the MindsDB URL from environment variables or default to localhost."""
    mindsdb_host = os.getenv('MINDSDB_HOST', '127.0.0.1')
    mindsdb_port = os.getenv('MINDSDB_PORT', '47334')
    mindsdb_url = f"http://{mindsdb_host}:{mindsdb_port}"
    print(f"Using MindsDB URL: {mindsdb_url}")
    return mindsdb_url

def create_skill(project_name: str, skill_name: str, skill_type: str, source: str, database: str, tables: list[str], description: str) -> dict:
    """
    Create a skill in a specified MindsDB project.

    Args:
        project_name (str): The name of the project where the skill resides.
        skill_name (str): The name of the skill to create.
        skill_type (str): The type of skill ('text2sql' or 'knowledge_base').
        source (str): Source for knowledge_base skill or empty for text2sql.
        database (str): Data source connection for text2sql skill.
        tables (list[str]): List of table names for text2sql skill.
        description (str): Description of the skill.

    Returns:
        dict: The response from the API containing the created skill's details.

    Raises:
        requests.exceptions.RequestException: If the API request fails.
    """
    base_url = connect_to_mindsdb()
    url = f"{base_url}/api/projects/{project_name}/skills"

    payload = {
        "skill": {
            "name": skill_name,
            "type": skill_type,
            "source": source,
            "database": database,
            "tables": tables,
            "description": description
        }
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error creating skill: {str(e)}")
        if response is not None:
            print(f"Response: {response.text}")
        raise

def create_chatbot(project_name: str, chatbot_name: str, database_name: str, agent_name: str) -> dict:
    """
    Create a chatbot in a specified MindsDB project.

    Args:
        project_name (str): The name of the project where the chatbot resides.
        chatbot_name (str): The name of the chatbot to create.
        database_name (str): Name of the connection to a chat app (e.g., Slack, MS Teams).
        agent_name (str): Name of the pre-created agent or empty if using model_name.

    Returns:
        dict: The response from the API containing the created chatbot's details.

    Raises:
        requests.exceptions.RequestException: If the API request fails.
    """
    base_url = connect_to_mindsdb()
    url = f"{base_url}/api/projects/{project_name}/chatbots"

    payload = {
        "chatbot": {
            "name": chatbot_name,
            "database_name": database_name,
            "agent_name": agent_name
        }
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error creating chatbot: {str(e)}")
        if response is not None:
            print(f"Response: {response.text}")
        raise

def get_chatbot(project_name: str, chatbot_name: str) -> dict:
    """
    Retrieve details of a chatbot in a specified MindsDB project.

    Args:
        project_name (str): The name of the project where the chatbot resides.
        chatbot_name (str): The name of the chatbot to retrieve.

    Returns:
        dict: The response from the API containing the chatbot's details.

    Raises:
        requests.exceptions.RequestException: If the API request fails.
    """
    base_url = connect_to_mindsdb()
    url = f"{base_url}/api/projects/{project_name}/chatbots/{chatbot_name}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving chatbot: {str(e)}")
        if response is not None:
            print(f"Response: {response.text}")
        raise