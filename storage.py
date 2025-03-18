"""
Storage module for loading and saving application data.

This module provides functions to persistently store and retrieve script and endpoint data
in a JSON file.
"""

import json

SAVE_FILE = "data.json"


def load_data():
    """
    Load data from the JSON save file.

    If the file does not exist or contains invalid JSON, a default structure is returned.

    :return: Dictionary containing stored scripts and endpoints.
    """
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"scripts": {}, "endpoints": {}}


def save_data(data):
    """
    Save data to the JSON file.

    :param data: Dictionary containing scripts and endpoints to be stored.
    """
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
