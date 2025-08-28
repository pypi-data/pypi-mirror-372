"""API request utilities for engine and studio commands."""

from typing import Dict, Optional

import requests
import typer

from .aws_utils import get_api_url
from .constants import console


def make_api_request(
    method: str,
    endpoint: str,
    json_data: Optional[Dict] = None,
    params: Optional[Dict] = None,
) -> requests.Response:
    """Make an API request with error handling."""
    api_url = get_api_url()
    url = f"{api_url}{endpoint}"

    try:
        if method == "GET":
            response = requests.get(url, params=params)
        elif method == "POST":
            response = requests.post(url, json=json_data)
        elif method == "DELETE":
            response = requests.delete(url)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        return response
    except requests.exceptions.RequestException as e:
        console.print(f"[red]❌ API request failed: {e}[/red]")
        raise typer.Exit(1)


def get_user_studio(username: str) -> Optional[Dict]:
    """Get the current user's studio."""
    response = make_api_request("GET", "/studios")
    if response.status_code != 200:
        return None

    studios = response.json().get("studios", [])
    user_studios = [s for s in studios if s["user"] == username]

    return user_studios[0] if user_studios else None
