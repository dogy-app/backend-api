import os
import requests
from dotenv import load_dotenv

load_dotenv()

ASSISTANT_API_ENDPOINT = os.getenv("ASSISTANT_API_ENDPOINT")

assistant_url = f"{ASSISTANT_API_ENDPOINT}/assistants"
headers = {"Content-Type": "application/json"}


def create_assistant():
    """
    Create a new assistant
    """
    payload = {
        "graph_id": "dogy_agent",
        "name": "Dogy",
    }

    response = requests.post(assistant_url, json=payload, headers=headers)
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        print(response.text)
        response.raise_for_status()


def search_assistant():
    """
    Search for existing assistants
    """
    payload = {"limit": 3}
    response = requests.post(f"{assistant_url}/search", headers=headers, json=payload)
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        print(response.text)
        response.raise_for_status()


def delete_assistant(assistant_id: str):
    """
    Delete an assistant by its ID
    """
    response = requests.delete(f"{assistant_url}/{assistant_id}", headers=headers)
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        print(response.text)
        response.raise_for_status()
