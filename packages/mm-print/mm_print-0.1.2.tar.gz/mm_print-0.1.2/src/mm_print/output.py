import sys
from collections.abc import Callable, Mapping
from typing import Any, NoReturn

import rich
import tomlkit
from mm_std import json_dumps
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table


def fatal(message: str, code: int = 1) -> NoReturn:
    """Print error message and exit with code."""
    print(message, file=sys.stderr)  # noqa: T201
    sys.exit(code)


def print_plain(messages: object) -> None:
    """Print to stdout without any formatting."""
    print(messages)  # noqa: T201


def print_json(data: object, type_handlers: dict[type[Any], Callable[[Any], Any]] | None = None) -> None:
    """Print object as formatted JSON."""
    rich.print_json(json_dumps(data, type_handlers=type_handlers))


def print_table(title: str, columns: list[str], rows: list[list[Any]]) -> None:
    """Print data as a formatted table."""
    table = Table(*columns, title=title)
    for row in rows:
        table.add_row(*(str(cell) for cell in row))
    console = Console()
    console.print(table)


def print_toml(
    *, toml: str | None = None, data: Mapping[str, Any] | None = None, line_numbers: bool = False, theme: str = "monokai"
) -> None:
    """Print TOML with syntax highlighting.

    Args:
        toml: TOML string to print. Either this or data must be provided.
        data: Object to serialize to TOML. Either this or toml must be provided.
        line_numbers: Whether to show line numbers.
        theme: Syntax highlighting theme.
    """
    if (toml is None) == (data is None):
        msg = "Exactly one of 'toml' or 'data' must be provided"
        raise ValueError(msg)

    toml_string = tomlkit.dumps(data) if data is not None else toml
    if toml_string is None:
        msg = "Internal error: toml_string should not be None"
        raise RuntimeError(msg)

    console = Console()
    syntax = Syntax(toml_string, "toml", theme=theme, line_numbers=line_numbers)
    console.print(syntax)
