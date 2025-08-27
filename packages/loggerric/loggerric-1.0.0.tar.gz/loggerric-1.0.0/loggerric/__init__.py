from loggerric._progress_bar import ProgressBar
from loggerric._log_levels import LogLevel
from loggerric._prompt import prompt
from loggerric._timer import Timer
from loggerric._log import Log
from colorama import init

# Add option to turn on feedback loop in prompt with options

# Expose these functions/classes
__all__ = ['LogLevel', 'prompt', 'ProgressBar', 'Log', 'Timer']

# Initialize Colorama
init(autoreset=True)