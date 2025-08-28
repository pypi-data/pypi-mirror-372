import json
from typing import Dict, Optional
import requests


class AuthenCard:
    def __init__(self, token: str, api_url: str):
        """
        Initialize the Authen class with a secret key for JWT signing.

        Args:
            token: The JWT token to authenticate with the AuthenCard
            api_url: The API URL of the AuthenCard API
        """
        self.token = token
        self.api_url = api_url

    @classmethod
    def from_config(cls, config_path: str = "authen/secret.json"):
        """
        Initialize UserGenerator instance from a JSON configuration file.

        Args:
            config_path: Path to the JSON configuration file (default: authen/secret.json).
        Returns:
            An instance of UserGenerator with values loaded from the config file.
        Raises:
            FileNotFoundError: If the config file doesn't exist.
            KeyError: If required fields are missing in the config file.
            json.JSONDecodeError: If the config file is invalid JSON.
        """
        try:
            with open(config_path, "r") as f:
                config = json.load(f)

            required_fields = ["token", "api_url"]
            missing_fields = [field for field in required_fields if field not in config]
            if missing_fields:
                raise KeyError(f"Missing required fields in config: {missing_fields}")

            return cls(
                token=config["token"],
                api_url=config["api_url"],
            )
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found at: {config_path}")
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Invalid JSON in config file: {e}", e.doc, e.pos
            )

    def verify_access_token(
        self, token: str = None, api_url: str = "http://localhost:8000/verify-token"
    ) -> Optional[Dict]:
        """
        Verify a JWT access token by sending a request to the FastAPI verify-token endpoint.

        Args:
            token (str): The JWT token to verify
            api_url (str): The URL of the FastAPI verify-token endpoint (default: http://localhost:8000/verify-token)

        Returns:
            Optional[Dict]: Token payload with username, expires, and issued_at if valid, None if invalid

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        actual_token = token or self.token
        actual_api_url = api_url or self.api_url
        headers = {"Content-Type": "application/json"}
        body = {"access_token": actual_token, "token_type": "Bearer"}

        try:
            response = requests.post(actual_api_url, json=body, headers=headers)
            response.raise_for_status()  # Raises HTTPError for bad responses
            is_valid_token = True if response.status_code == 200 else False
            return is_valid_token

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            return None
        except requests.exceptions.RequestException as err:
            print(f"Error occurred while verifying token: {err}")
            return None


# if __name__ == "__main__":
#     # 1. Load config.json file
#     with open("authen/secret.json", "r") as f:
#         config = json.load(f)

#     # 2. Get secret key and token
#     token = config["token"]

#     # 3. Initialize
#     api_url = "http://localhost:8000/verify-token"
#     auth = AuthenCard(
#         token=token,
#         api_url=api_url
#     )

#     # 4. Verify token
#     is_enable_access = auth.verify_access_token()

#     return_message = "This is a valid access token" if is_enable_access else "This is an invalid access token"
#     print(return_message)
