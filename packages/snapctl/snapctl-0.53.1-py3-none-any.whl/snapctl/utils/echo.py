"""
This module contains functions to print messages to the console.
"""
import json
import typer
from rich import print
from rich.markup import escape
from snapctl.config.constants import SNAPCTL_ERROR
from snapctl.types.definitions import ErrorResponse
# Run `python -m rich.emoji` to get a list of all emojis that are supported


def _stringify_message(msg: object) -> str:
    if isinstance(msg, (dict, list)):
        return json.dumps(msg, indent=2)
    return str(msg)


def error(msg: object, code: int = SNAPCTL_ERROR, data: object = None) -> None:
    """
    Prints an error message to the console.
    """
    msg = _stringify_message(msg)
    error_response = ErrorResponse(
        error=True, code=code, msg=msg, data=data if data else ''
    )
    print(f"[bold red]Error[/bold red] {escape(msg)}")
    typer.echo(json.dumps(error_response.to_dict()), err=True)


def warning(msg: object) -> None:
    """
    Prints a warning message to the console.
    """
    msg = _stringify_message(msg)
    print(f"[bold yellow]Warning[/bold yellow] {escape(msg)}")


def info(msg: object) -> None:
    """
    Prints an info message to the console.
    """
    msg = _stringify_message(msg)
    print(f"[bold blue]Info[/bold blue] {escape(msg)}")


def success(msg: object) -> None:
    """
    Prints a success message to the console.
    """
    msg = _stringify_message(msg)
    print(f"[bold green]Success[/bold green] {escape(msg)}")
