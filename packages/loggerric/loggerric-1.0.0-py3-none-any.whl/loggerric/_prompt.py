from colorama import Fore
from loggerric._utils import *

def prompt(question:str, options:list[str]=[], default:str=None) -> str | None:
    """
    **Prompts standard I/O and returns the answer.**

    If options are given but not chosen by the user during prompting, return value will be `None`

    *Parameters*:
    - `question` (str): The question appearing in the prompt.
    - `options` (list[str]): Options that the user can pick from during prompting.
    - `default` (str): If options are not `None`, optionally specify a default value.

    *Example (No Options)*:
    ```python
    answer = prompt(question='Insert your name')
    ```

    *Example (Options)*:
    ```python
    answer = prompt(question="What's the best?", options=['a', 'b', 'c'], default='b')
    ```
    """
    # If no options ommitted prompt immediately
    if len(options) == 0:
        return input(f'{Fore.BLUE}{question}: {Fore.CYAN}') or None

    # Format options
    options_formatted = f'{Fore.BLUE} | '.join(Fore.YELLOW + o for o in options)

    # Prompt user
    answer = input(f'{Fore.MAGENTA}[{timestamp()}] {Fore.BLUE}{question} [ {options_formatted}{Fore.BLUE} ]{f" ({Fore.YELLOW}{default}{Fore.BLUE})" if default else ""}:{Fore.CYAN} ')

    # Validate answer
    if len(answer) == 0 and default != None:
        return default
    if answer in options:
        return answer
    
    # Implementor decides what to happen if user answers "wrong"
    return None