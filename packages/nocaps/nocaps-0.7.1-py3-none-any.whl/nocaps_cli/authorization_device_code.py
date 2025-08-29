import requests
import time
import keyring
from dotenv import load_dotenv
import os

# ! This file is deprecated

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../.env'))

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")  # e.g. "dev-1234.us.auth0.com"
CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUDIENCE = os.getenv("AUTH0_AUDIENCE")
SCOPE = os.getenv("AUTH0_SCOPE")

SERVICE_NAME = "nocaps-auth0"   # identifier for keyring storage
ACCESS_TOKEN_KEY = "access_token"
REFRESH_TOKEN_KEY = "refresh_token"

def save_tokens(access_token: str, refresh_token: str | None = None):
  """
  Save access and refresh tokens to keyring.

  Args:
      access_token (str): The access token to save.
      refresh_token (str | None, optional): The refresh token to save. Defaults to None.

  Returns:
      None
  """
  keyring.set_password(SERVICE_NAME, ACCESS_TOKEN_KEY, access_token)
  if refresh_token:
    keyring.set_password(SERVICE_NAME, REFRESH_TOKEN_KEY, refresh_token)

def load_tokens():
  """
  Load access and refresh tokens from keyring.

  Returns:
    tuple[str | None, str | None]: A tuple containing the access token and refresh token, or None if not found.
  """
  access_token = keyring.get_password(SERVICE_NAME, ACCESS_TOKEN_KEY)
  refresh_token = keyring.get_password(SERVICE_NAME, REFRESH_TOKEN_KEY)
  return access_token, refresh_token

#TODO Rewire this function
def refresh_access_token(refresh_token: str | None):
  """
  Requests Auth0 for a new access token using the refresh token.

  If the request is successful, the new access token is saved.
  If the request fails, the user is prompted to re-authenticate.

  Args:
    refresh_token (str | None): The refresh token to use for obtaining a new access token.

  Returns:
      None
  """

  # Starts the authentication process if refresh token is not available
  if refresh_token is None:
    start_auth_verification_process()
    return

  # If refresh token is available, request a new access token
  url = f"https://{AUTH0_DOMAIN}/oauth/token"
  data: dict[str, str | None] = {
    "client_id": CLIENT_ID,
    "grant_type": "refresh_token",
    "refresh_token": refresh_token
  }
  resp = requests.post(url, data=data).json()

  # If the request is successful, save the new access token
  # If the request fails (meaning the refresh token is invalid/expired), the user is prompted to re-authenticate.
  if "access_token" in resp:
      save_tokens(resp["access_token"])
  else:
      start_auth_verification_process()

def request_user_code():

  """
  Requests Auth0 for device authorization and prompts user to visit the verification URI with device code.

  Raises:
    Exception: If the request fails.

  Returns:
    tuple[str, int]: A tuple containing the device code and polling interval.
  """

  url = f"https://{AUTH0_DOMAIN}/oauth/device/code"
  data = {
    "client_id": CLIENT_ID,
    "scope": SCOPE,
    "audience": AUDIENCE
  }
  resp = requests.post(url, data=data).json()

  if "error" in resp:
    raise Exception(f"Failed to request user code: {resp}")

  device_code = resp["device_code"]
  user_code = resp["user_code"]
  verification_uri_complete = resp["verification_uri_complete"]
  interval = resp.get("interval", 5)

  print(f"Please visit {verification_uri_complete} and enter the code: {user_code}")


  return device_code, interval

def poll_for_tokens(device_code: str, interval: int):
  """
  Keep checking (Polls) the Auth0 token endpoint for tokens using the device code.

  Poll the Auth0 token endpoint for tokens using the device code. Prints the status of the authorization.

  Args:
      device_code (str): The device code returned by the Auth0 device authorization endpoint.
      interval (int): The interval returned by the Auth0 device authorization endpoint in seconds.

  Raises:
      Exception: If the polling fails or the user is not authorized.

  Returns:
      None
  """

  token_url = f"https://{AUTH0_DOMAIN}/oauth/token"
  while True:
    time.sleep(interval)
    token_data: dict[str, str | None] = {
      "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
      "device_code": device_code,
      "client_id": CLIENT_ID
    }
    token_resp = requests.post(token_url, data=token_data).json()

    if "error" in token_resp:
      if token_resp["error"] == "slow_down":
        interval += 5
      else:
        raise Exception(f"Auth failed: {token_resp}")
    else:
      print("✅ Login successful!")
      save_tokens(token_resp["access_token"], token_resp.get("refresh_token"))
      break

def start_auth_verification_process():
  """
  Redirect the user to the Auth0 verification URI and start polling

  Returns:
      None
  """
  device_code, interval = request_user_code()
  poll_for_tokens(device_code, interval)

if __name__ == "__main__":
    
  keyring.delete_password(SERVICE_NAME, ACCESS_TOKEN_KEY)
  keyring.delete_password(SERVICE_NAME, REFRESH_TOKEN_KEY)

  # tokens = device_authorization()
  # print(tokens)