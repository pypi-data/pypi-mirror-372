# loggerric

**loggerric** is a lightweight Python utility library providing advanced logging, progress bars, timers, and user prompts for CLI applications. It offers colorful, formatted output to make debugging and tracking easier.

---

## Features

- **Timers**: Measure execution time of code snippets.
- **Logging**: Structured logging with levels: `INFO`, `WARN`, `ERROR`, `DEBUG`.
- **Progress Bars**: Real-time CLI progress bars with ETA calculations.
- **Prompts**: Interactive user input with optional choices and defaults.

---

## Installation

```bash
pip install loggerric
```

---

## Usage

### Timer

```python
from loggerric import Timer
from time import sleep

with Timer(name='Processing'):
    sleep(1.5)
```

### Logging

```python
from loggerric import Log, LogLevel

Log.info("This is an info message")
Log.warn("This is a warning")
Log.error("This is an error")
Log.debug("This is a debug message")

# Enable or disable specific logging levels
Log.disable(LogLevel.DEBUG)
Log.enable(LogLevel.DEBUG)
```

### Progress Bar

```python
from loggerric import ProgressBar
from time import sleep

end_val = 50
bar = ProgressBar(end_value=end_val, name='Downloading', bar_length=40)
for i in range(1, end_val + 1):
    sleep(0.05)
    bar.update(i)
```

### Prompt

```python
from loggerric import prompt

# Simple input
name = prompt("Enter your name")

# Input with options
choice = prompt("Choose a letter", options=['a', 'b', 'c'], default='b')
```

---

## API Reference

#### `Timer(name: str = 'Timer')`
- Context manager for measuring execution time.
- **Methods**: `__enter__`, `__exit__`.

#### `Log`
- Logging class with methods: `info`, `warn`, `error`, `debug`.
- Enable/disable levels dynamically.

#### `ProgressBar(end_value: int, name: str = 'Progress', bar_length: int = 50)`
- CLI progress bar with ETA.
- **Methods**: `update(current_value: int)`.

#### `prompt(question: str, options: list[str] = [], default: str = None)`
- Interactive input prompt with optional predefined choices.

#### `LogLevel`
- Enum defining log levels: `INFO`, `WARN`, `ERROR`, `DEBUG`.

---

## Contributing

Contributions are welcome! Feel free to submit pull requests or report issues.

---

## License

This project is licensed under the MIT License.