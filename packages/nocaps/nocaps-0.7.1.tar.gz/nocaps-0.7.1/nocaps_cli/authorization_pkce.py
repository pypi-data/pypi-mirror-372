import base64
import hashlib
import secrets
import keyring
import webbrowser
import threading
import http.server
import socketserver
import requests

AUTH_DOMAIN = "dev-g8fu3wxgsdujf3e2.us.auth0.com"  # e.g., "mytenant.auth0.com"
CLIENT_ID = "yuQNsXKeN6SHiP2LHasHdrl3MPdHB1we"
REDIRECT_URI = "http://localhost:8000/callback"
AUTH_URL = f"https://{AUTH_DOMAIN}/authorize"
TOKEN_URL = f"https://{AUTH_DOMAIN}/oauth/token"
AUDIENCE = "https://nocaps.com"  # Optional: only if using an API
SCOPES = "openid profile email offline_access"

# identifier for keyring storage
SERVICE_NAME = "nocaps-auth0"
ACCESS_TOKEN_KEY = "access_token"
REFRESH_TOKEN_KEY = "refresh_token"

# global variable to capture code
auth_code = None

def generate_code_verifier(length:int=64):
  """
  Generate a code verifier (Random string) for PKCE.

  Args:
      length (int, optional): The length of the code. Defaults to 64.

  Returns:
      str: The generated code verifier.
  """
  return base64.urlsafe_b64encode(secrets.token_bytes(length)).rstrip(b'=').decode('utf-8')

def generate_code_challenge(verifier: str) -> str:
  """
  Generate a code challenge from the code verifier for PKCE.

  Args:
      verifier (str): The code verifier.

  Returns:
      str: The Generated Code challenge (Base64 URL-encoded SHA256 hash of the code verifier)
  """
  # verifier.encode('utf-8') converts string into sequence of bytes.
  # hashlib.sha256(bytes) takes the bytes and prepares to compute a hash.
  # .digest() computes the hash and returns it as bytes.
  hashed = hashlib.sha256(verifier.encode('utf-8')).digest()
  # base64.urlsafe_b64encode encodes the bytes to base64, making it URL-safe.
  return base64.urlsafe_b64encode(hashed).rstrip(b'=').decode('utf-8')

class OAuthCallbackHandler(http.server.SimpleHTTPRequestHandler):
  def do_GET(self):
    """
    Handle GET requests for the OAuth callback.

    Extract and store the authorization code.
    """
    global auth_code
    if self.path.startswith("/callback"):
      # Extract 'code' from query string
      query = self.path.split("?", 1)[-1]
      params = dict(qc.split("=") for qc in query.split("&"))
      auth_code = params.get("code")

      # Respond to browser
      self.send_response(302)
      self.send_header("Location", "https://nocaps.moinuddin.tech/login")
      self.end_headers()
    else:
      self.send_response(404)
      self.end_headers()
  def log_message(self, format: str, *args: object):
    pass

def start_server():
  """
  Start a simple HTTP server to handle the OAuth callback.
  """
  with socketserver.TCPServer(("localhost", 8000), OAuthCallbackHandler) as httpd:
    httpd.handle_request()  # handle one request then exit

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

def generate_auth_url_and_launch_server(code_challenge: str):
  """
  Build the authorization URL and start the local server and open the browser for login.

  Args:
      code_challenge (str): The code challenge generated from the code verifier.

  Returns:
      None
  """
  params = {
    "audience": AUDIENCE,
    "scope": SCOPES,
    "response_type": "code",
    "client_id": CLIENT_ID,
    "redirect_uri": REDIRECT_URI,
    "code_challenge": code_challenge,
    "code_challenge_method": "S256"
  }
  
  auth_request_url = AUTH_URL + "?" + "&".join([f"{k}={v}" for k, v in params.items()])

  # Step 3: open browser and start local server
  server_thread = threading.Thread(target=start_server, daemon=True)
  server_thread.start()

  print(f"""Opening browser to complete login...

  if you are not redirected automatically, please click the link below:

  {auth_request_url}
        """)
  webbrowser.open(auth_request_url)

  # Wait for user to login and server to catch the code
  server_thread.join()

def exchange_code_for_tokens(code_verifier: str):
  """
  Exchange the authorization code for access and refresh tokens.

  Requests the Identity Provider's token endpoint for tokens in exchange for the authorization code.
  Later, it saves the tokens securely.

  Args:
      code_verifier (str): The code verifier used in the initial request.
  """
  data: dict[str, str | None] = {
    "grant_type": "authorization_code",
    "client_id": CLIENT_ID,
    "code": auth_code,
    "redirect_uri": REDIRECT_URI,
    "code_verifier": code_verifier
  }

  response = requests.post(TOKEN_URL, data=data)
  response.raise_for_status()
  tokens = response.json()
  save_tokens(tokens.get("access_token"), tokens.get("refresh_token"))

def start_auth_verification_process():
  """Start the authentication verification process.

  Step 1: Generate code verifier and code challenge.
  Step 2: Build authorization URL and start local server.
  Step 3: Exchange authorization code for tokens.

  Raises:
      Exception: If the authorization code is not obtained.
  """
  global auth_code
  code_verifier = generate_code_verifier()
  code_challenge = generate_code_challenge(code_verifier)

  generate_auth_url_and_launch_server(code_challenge)

  if not auth_code:
    raise Exception("Failed to get authorization code.")

  exchange_code_for_tokens(code_verifier)

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
  url = TOKEN_URL
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

if __name__ == "__main__":
  start_auth_verification_process()