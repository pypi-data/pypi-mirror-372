import re
import requests

from typing import Union
from functools import wraps
from pyrogram import Client, filters

from d4rk.Logs import setup_logger
from d4rk.Utils import clear_terminal

logger = setup_logger(__name__)

command_registry = []

def get_priority(description: str) -> int:
    desc_lower = description.lower()
    if "(owner only)" in desc_lower:
        return 4
    elif "(sudo only)" in desc_lower:
        return 3
    elif "(admin only)" in desc_lower:
        return 2
    else:
        return 1

def reorder_command_registry():
    global command_registry
    command_registry.sort(key=lambda cmd: get_priority(cmd["description"]))

def get_commands():
    return command_registry

def command(command: Union[str, list], description: str):
    def decorator(func):
        command_registry.append({
            "command": command,
            "description": description,
            "handler": func
        })
        logger.info(f"Registered command: {command} - {description}")
        @Client.on_message(filters.command(command))
        @wraps(func)
        async def wrapper(client, message):
            return await func(client, message)
        reorder_command_registry()
        clear_terminal()
        return wrapper
    return decorator

class CommandAI:
    def __init__(self):
        self.api_key = "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"
        self.api_url = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
        self.headers = {"Authorization": "Bearer " + self.api_key}

    def __post(self,payload):   
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        if response.status_code != 200:
            print(f"❌ Error {response.status_code}: {response.text}")
            return None
        return response.json()
    
    def extract_username(self, query: str):
        match = re.search(r'@[\w\d_]+', query)
        return match.group(0) if match else None

    def get_command(self,user_query):
        labels = [entry["description"] for entry in command_registry]
        response = self.__post(
            payload={
                "inputs": user_query,
                "parameters": {"candidate_labels": labels},
            }
        )
        print(response)
        if response is None:return None
        best_label = response["labels"][0]
        if best_label is None:
            logger.error("No matching command found for the user query.")
            return None
        for entry in command_registry:
            if entry["description"] == best_label:
                return entry["command"] if isinstance(entry["command"], str) else entry["command"][0]
        return None

find_command = CommandAI()
