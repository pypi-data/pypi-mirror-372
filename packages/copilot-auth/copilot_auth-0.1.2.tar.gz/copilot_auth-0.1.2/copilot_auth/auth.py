# Authenticator to get github copilot token using device flow
import warnings

import requests
import time
import os
import typing


# The client ID is specific to GitHub and the device flow for Copilot.
# It is used by various Copilot clients to initiate authentication.
GITHUB_CLIENT_ID = "Iv1.b507a08c87ecfe98"
HEADERS = {
    "accept": "application/json",
    "editor-version": "Neovim/0.6.1",
    "editor-plugin-version": "copilot.vim/1.16.0",
    "content-type": "application/json",
    "user-agent": "GitHubCopilot/1.155.0",
    "accept-encoding": "gzip,deflate,br"
}

def get_gh_client_id():
    return os.getenv("GITHUB_CLIENT_ID", GITHUB_CLIENT_ID)


def get_access_token():
    """Starts the GitHub device flow and gets a user-scoped access token."""

    gh_client_id = get_gh_client_id()

    # Step 1: Request a device and user verification code and expiration time
    response = requests.post(
        "https://github.com/login/device/code",
        headers=HEADERS,
        json={"client_id": gh_client_id, "scope": "read:user"}
    )
    response.raise_for_status()
    data = response.json()

    device_code = data.get("device_code")
    user_code = data.get("user_code")
    verification_uri = data.get("verification_uri")
    interval = data.get("interval", 5)

    print(
        f"Please visit {verification_uri} and enter the code {user_code} to authenticate."
    )

    # Step 2: Poll for the user's authorization
    while True:
        time.sleep(interval)
        response = requests.post(
            "https://github.com/login/oauth/access_token",
            headers=HEADERS,
            json={
                "client_id": gh_client_id,
                "device_code": device_code,
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            }
        )
        response.raise_for_status()

        # Check if the user has authenticated
        if "access_token" in response.json():
            return response.json().get("access_token")

def get_copilot_token(access_token):
    """Uses the access token to get a short-lived Copilot-specific token."""
    print("Fetching Copilot token...")
    response = requests.get(
        "https://api.github.com/copilot_internal/v2/token",
        headers={
            **HEADERS,
            "authorization": f"token {access_token}"
        }
    )
    response.raise_for_status()
    return response.json().get("token")


# github access token and copilot token handling call back signature
class TokenHandler(typing.Protocol):
    def __call__(self, token): ...


class DefaultGHAccessTokenHandler(TokenHandler):
    def __call__(self, token):
        os.environ["GITHUB_ACCESS_TOKEN"] = token

class DefaultCopilotTokenHandler(TokenHandler):
    def __call__(self, token):
        os.environ["GITHUB_TOKEN"] = token

# fetch github access token if it is not present in the environment
def authenticate_github_access_token(handlers:list[TokenHandler]):
    if os.getenv("GITHUB_ACCESS_TOKEN"):
        warnings.warn("GITHUB_ACCESS_TOKEN is already set in the environment. Skipping authentication.")
        return
    access_token = get_access_token()
    handlers.append(DefaultGHAccessTokenHandler())
    for handler in handlers:
        handler(access_token)


# fetch copilot token if it is not present in the environment
def authenticate_copilot_token(handlers:list[TokenHandler], force_update=False):
    if not force_update and os.getenv("GITHUB_TOKEN"):
        warnings.warn("GITHUB_TOKEN is already set in the environment. Skipping authentication.")
        return
    access_token = os.getenv("GITHUB_ACCESS_TOKEN")
    if not access_token:
        raise ValueError("GITHUB_ACCESS_TOKEN is not set. Please authenticate first for github access token.")
    copilot_token = get_copilot_token(access_token)
    handlers.append(DefaultCopilotTokenHandler())
    for handler in handlers:
        handler(copilot_token)
