import requests
import getpass
import json
import os
from keycloak import KeycloakOpenID

TOKEN_CACHE_FILE = ".token_cache"


def load_token_cache(server: str):
    """Load the token cache for a specific server from a file."""

    if os.path.exists(TOKEN_CACHE_FILE):
        with open(TOKEN_CACHE_FILE, "r") as file:
            cache = json.load(file)
            return cache.get(server, None)
    return None


def save_token_cache(server: str, token_data):
    """Save the token cache for a specific server to a file."""

    if os.path.exists(TOKEN_CACHE_FILE):
        with open(TOKEN_CACHE_FILE, "r") as file:
            cache = json.load(file)
    else:
        cache = {}
    cache[server] = token_data
    with open(TOKEN_CACHE_FILE, "w") as file:
        json.dump(cache, file)


def get_token_from_cache(server: str, keycloak_openid: KeycloakOpenID):
    """
    Retrieve and refresh the token for a specific server from the cache.
    Returns the refreshed access token if available, else None.
    """

    token_data = load_token_cache(server)
    if token_data:
        try:
            new_token_data = keycloak_openid.refresh_token(
                token_data["refresh_token"]
            )
            save_token_cache(server, new_token_data)
            return new_token_data["access_token"]
        except Exception:
            print(
                f"Failed to refresh token for {server}, retrieving a new one."
            )
    return None


def get_new_token(server: str, keycloak_openid: KeycloakOpenID) -> str:
    """Prompt for credentials and obtain a new JWT token."""

    username = input(f"Enter your username for {server}: ")
    password = getpass.getpass(f"Enter your password for {server}: ")
    token_data = keycloak_openid.token(username, password)
    save_token_cache(server, token_data)
    return token_data["access_token"]


def get_jwt_token(server: str) -> str:
    """
    Authenticate with Keycloak using caching. If a cached token is available
    and can be refreshed, use it.

    Otherwise, prompt for credentials and return a new token.
    """
    # Retrieve Keycloak configuration from the server
    response = requests.get(f"{server}/api/config")
    response.raise_for_status()
    keycloak_config = response.json()

    # Initialize the Keycloak OpenID client using the configuration details
    keycloak_openid = KeycloakOpenID(
        server_url=keycloak_config["url"],
        client_id=keycloak_config["clientId"],
        realm_name=keycloak_config["realm"],
        verify=True,
    )

    # Try to retrieve and refresh token from cache, else prompt for new credentials
    token = get_token_from_cache(server, keycloak_openid)
    if not token:
        token = get_new_token(server, keycloak_openid)
    return token
