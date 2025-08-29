from rich.console import Console
from subprocess import CalledProcessError
import threading

def thinking_animation(stop_loading : threading.Event) -> None:
  """
  Show a thinking animation while a task is in progress.

  Args:
      stop_loading (threading.Event): An event to signal when to stop the animation.

  Returns:
      None
  """
  from rich.panel import Panel
  from rich.live import Live
  from time import sleep

  message_base = 'Let me help you with this'
  i = 0
  panel = Panel(message_base, border_style='cyan')
  with Live(panel, refresh_per_second=4, transient=True) as live:
    while stop_loading.is_set() == False:
      dots = '.' * (i % 4)
      panel = Panel(f'{message_base}{dots}', border_style='cyan')
      live.update(panel)
      sleep(0.5)
      i += 1

stop_loading = threading.Event()
thread = None
console = Console()
api="https://api.nocaps.moinuddin.tech"

def start_animation():
  """
  Start the thinking animation.

  Returns:
      None
  """
  global thread
  stop_loading.clear()
  thread = threading.Thread(target=thinking_animation, args=(stop_loading,))
  thread.start()

def stop_animation():
  """
  Stop the thinking animation.

  Returns:
      None
  """
  global thread
  stop_loading.set()
  if thread is not None:
    thread.join()
    thread = None
  console.clear_live()

def prompt_and_authorize_the_api(prompt: str):
  """
  Prompt the user for API authorization (if required) and send the request to the API.

  Args:
      prompt (str): The prompt to send to the API.

  Returns:
      requests.Response: The response from the API.
  """
  import requests
  from .authorization_pkce import load_tokens, refresh_access_token
  
  access_token : str | None = load_tokens()[0]

  # Get a new access token if not available
  if access_token is None:
    stop_animation()
    refresh_access_token(load_tokens()[1])
    access_token = load_tokens()[0]

  response = requests.post(
    f"{api}/debug",
    json={"prompt": prompt},
    headers={"Authorization": f"Bearer {access_token}"}
  )

  # if the existing access token is invalid/expired, get a new access token
  if response.status_code == 401:
    stop_animation()
    refresh_access_token(load_tokens()[1])
    access_token = load_tokens()[0]

  response = requests.post(
    f"{api}/debug",
    json={"prompt": prompt},
    headers={"Authorization": f"Bearer {access_token}"}
  )
  
  return response

def fetch_api_response_with_validation(prompt: str):
  """
  Fetch the API response and validate the JSON structure.

  Args:
      prompt (str): The prompt to send to the API.

  Returns:
      str: The output from the API.

  Raises:
      Exception: If the API response is invalid or an error occurs.
  """
  data = None
  response = prompt_and_authorize_the_api(prompt)
  if hasattr(response, "json") and callable(response.json):
    try:
      data = response.json()
    except Exception:
      stop_animation()
      raise Exception(f"Failed to parse response from API, here's data: {response.text}")
  else:
    stop_animation()
    raise Exception("API response object does not have a json() method, here's data: {response.text}")

  if 'output' in data:
    return data['output']
  else:
    stop_animation()
    if 'error' in data:
      raise Exception(data['error'])
    else:
      raise Exception("Unexpected response format from API")

def handle_error(e : CalledProcessError, file_content : str):
  """
  Handle errors that occur during the execution of the code.

  Takes the file content and the error information to provide feedback using the API.

  Args:
      e (CalledProcessError): The error that occurred.
      file_content (str): The content of the file being processed.

  Returns:
      None
  """
  from rich import print
  
  start_animation()

  # prompting ai for response
  error = e.stderr
  file_text = file_content

  roast_prompt = f"""
    Analyze the following code written by a human developer. 
    Identify areas of inefficiency, poor style, potential bugs, 
    security vulnerabilities (if applicable), or just plain head-scratching choices. 
    Provide a concise, witty, and extremely insulting roast targeting these 
    specific issues within 12 words. Give only the roast for the output.

    ---

    {file_text}

    ---

    Example Roast Output:

    My Grandmother runs faster than your code.

    I've seen spaghetti with fewer tangles than your function calls.

    Your code runs like a drunk grandma on rollerblades — in reverse.

    I debugged it… turns out the real bug was you.
    """
  prompt = f"""{file_text}\n The above file is resulting in this error: {error} \nSuggest a fix, formatting the response in four paragraphs following this format:

    :thumbs_down: : 
    [red] [Indicate the *wrong* code snippet (if applicable)] [/red]
      
    [yellow] [Provide a breif explanation of the fix] [/yellow]

    :thumbs_up: : 
    [green] [Indicate the correct(the fix) code snippet (if applicable)] [/green]
      
    [cyan] [Suggest any short further enhancements or best practices under 30 words] [/cyan]
    """
  roast = fetch_api_response_with_validation(roast_prompt)
  prompt_response = fetch_api_response_with_validation(prompt)
  response = prompt_response.replace('```python\n', '')
  response = response.replace('\n```', '')

  stop_animation()

  print(f"\n[blue]{roast.strip()}[/blue]\n\nBut here's what you can do about it\n")
  print(response.strip() + "\n")

def main():
  from argparse import ArgumentParser, Namespace
  from subprocess import run

  # imports configuration
  parser = ArgumentParser()

  parser.usage = "Learn python better!!"

  # cli configuration
  
  parser.add_argument('filepath', help='Add the path to the file')

  parser.add_argument('-v', '--verbose', action='count', help='Adds verbose to output')
  args: Namespace = parser.parse_args()

  file_content = ''
  try:
    try:
      # checking if the the file runs
      with open(args.filepath, 'r', encoding='utf-8') as f:
        file_content = f.read()
    except Exception:
      print("[yellow]File is not found or supported.[/yellow]")
      return

    file_extention = args.filepath.split('.')[-1]
    #checking if the file is compatible
    match file_extention:
      case 'py':
        result = run(['python', args.filepath], capture_output=True, text=True, check=True)
      case 'js':
        result = run(['node', args.filepath], capture_output=True, text=True, check=True)
      case 'java':
        # Compile the Java file first
        run(['javac', args.filepath], capture_output=True, text=True)
        class_name = args.filepath.split('.')[-2].replace('\\', '').replace('/', '')
        result = run(['java', class_name], capture_output=True, text=True, check=True)
      case _:
        # If the file extension is not supported
        print(f"[yellow]File extension '.{file_extention}' is not supported.[/yellow]")
        return

    # print the output if there are not errors
    print(f"{result.stdout}")

  # debugging using the api
  except CalledProcessError as e:
    handle_error(e, file_content)
if __name__ == "__main__":
  main()