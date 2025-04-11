"""
Module for managing minds in MindsDB
"""
import os
from dotenv import load_dotenv
from openai import OpenAI

def get_client():
    """Get authenticated MindsDB client using API key from environment variables"""
    load_dotenv()
    minds_api_key = os.getenv('MINDS_API_KEY')
    
    if not minds_api_key:
        raise ValueError("MINDS_API_KEY not found in environment variables")
        
    # For this simple version, we won't use the Client SDK since we're using requests
    return OpenAI(
        api_key=minds_api_key,
    )

def create_mind(name, datasources, prompt_template=None, update=True):
    """
    Create a new Mind in MindsDB (Note: This still uses OpenAI client for simplicity)
    
    Args:
        name (str): Unique name for the Mind
        datasources (list): List of datasource names (strings)
        prompt_template (str, optional): Prompt template for the Mind
        update (bool, optional): Whether to update if the Mind already exists
        
    Returns:
        dict: Simulated mind creation response
    """
    client = get_client()
    
    load_dotenv()
    prompt_template = prompt_template or os.getenv('MIND_PROMPT_TEMPLATE', 
                                                 'Answer questions in a helpful way using the available data')
    
    # Since we're not using the SDK, we'll simulate this for now
    # In a full implementation, you'd POST to /api/minds, but MindsDB's OpenAI-compatible API is used here
    print(f"Simulating mind creation for '{name}' with datasources: {datasources}")
    return {"name": name, "datasources": datasources, "prompt_template": prompt_template}

def query_mind(mind_name, question):
    """
    Query a Mind created on MindsDB
    
    Args:
        mind_name (str): The name of the Mind to query
        question (str): The question to ask the Mind
        
    Returns:
        str: The response from the Mind
    """
    client = get_client()
    
    print('Answering the question may take up to 30 seconds...')
    
    try:
        completion = client.chat.completions.create(
            model=mind_name,
            messages=[{'role': 'user', 'content': question}],
            stream=False
        )
        return completion.choices[0].message.content
    except Exception as e:
        raise Exception(f"Error querying Mind: {str(e)}")