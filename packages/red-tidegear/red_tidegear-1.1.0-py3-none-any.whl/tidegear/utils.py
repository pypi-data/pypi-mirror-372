# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
# © 2025 cswimr

"""A collection of useful utility functions and classes, to reduce repetitiveness between cogs."""

import inspect
import os
from contextlib import contextmanager
from datetime import datetime
from enum import StrEnum
from importlib.resources import as_file, files
from importlib.util import find_spec
from typing import Any, Callable, Generator

import discord
from discord.utils import MISSING
from red_commons.logging import RedTraceLogger
from redbot.core import commands
from redbot.core.commands.context import TICK
from redbot.core.utils import chat_formatting as cf

TRUE: str = TICK
"""The emoji used for [`ctx.tick()`][redbot.core.commands.Context.tick] calls, and for truthy values in [`tidegear.utils.get_bool_emoji`][].
Corresponds to `redbot.core.commands.context.Tick`.
"""
FALSE: str = "\N{NO ENTRY SIGN}"
"""The emoji used for falsy values in [`tidegear.utils.get_bool_emoji`][]."""
NONE: str = "\N{BLACK QUESTION MARK ORNAMENT}\N{VARIATION SELECTOR-16}"
"""The emoji used for NoneType values in [`tidegear.utils.get_bool_emoji`][]."""


@contextmanager
def set_env(
    key: str,
    value: str | None,
    logger: RedTraceLogger | None = None,
) -> Generator[None, Any, None]:
    """Temporarily set or unset an environment variable, then restore old value or delete on exit.

    Example:
        ```python
        import os
        from tidegear.utils import set_env


        def hello_world():
            return os.environ.get("HELLO_WORLD")


        with set_env(key="HELLO_WORLD", value="hello world"):
            print(hello_world())  # hello world

        print(hello_world())  # None
        ```

    Args:
        key: The environment variable to set.
        value: The content you want to set the environment variable to.
            If this is None, the environment variable will be deleted if it exists.
        logger: The logger to use to log the environment variables. Logs at `TRACE` level.
    """
    old_value = os.environ.get(key)
    if logger:
        logger.trace("Setting '%s' -> '%s'", key, value)
    if value:
        os.environ[key] = value
    elif os.environ.get(key):
        del os.environ[key]

    try:
        yield
    finally:
        if logger:
            logger.trace("Restoring '%s' -> '%s'", key, value)
        if old_value:
            os.environ[key] = old_value
        elif os.environ.get(key):
            del os.environ[key]


def class_overrides_method(child: type, parent: type, method_name: str) -> bool:
    """Check whether or not a child class overrides a method from a parent class.

    Args:
        child (type): The child class to check against.
        parent (type): The parent class to check against.
        method_name (str): The name of the method to check for.

    Raises:
        TypeError: If the `child` class is not a subclass of `parent`.

    Returns:
        Whether or not the method specified is overridden on `child`.
    """
    if not issubclass(child, parent):
        msg = f"{child.__name__} is not a subclass of {parent.__name__}!"
        raise TypeError(msg)

    child_attr = inspect.getattr_static(obj=child, attr=method_name, default=None)
    parent_attr = inspect.getattr_static(obj=parent, attr=method_name, default=None)
    return child_attr is not parent_attr


def get_bool_emoji(value: bool | None) -> str:
    """Return a unicode emoji based on a boolean value.

    Example:
        ```python
        from tidegear.utils import get_bool_emoji

        print(get_bool_emoji(True))  # ✅
        print(get_bool_emoji(False))  # 🚫
        print(get_bool_emoji(None))  # ❓️
        ```

    Args:
        value: The boolean value to check against.

    Returns:
        The corresponding unicode emoji.
    """
    match value:
        case True:
            return TRUE
        case False:
            return FALSE
        case _:
            return NONE


def get_asset_as_file(*, package: str = "tidegear.assets", filename: str, description: str | None = None, spoiler: bool = MISSING) -> discord.File:
    """Create a [`discord.File`][] from a file within a Python package.

    Args:
        package: The package to retrieve the file from.
        filename: The name of the file you'd like to retrieve. Does not support subpaths.
        description: The description of the uploaded file on Discord, used by screen readers.
        spoiler: Whether or not to mark the image as a spoiler on Discord.

    Raises:
        ImportError: Raised if the package provided cannot be found.
        FileNotFoundError: Raised if the filename provided does not exist within the provided package.

    Returns:
        The resulting object.
    """
    if not find_spec(name=package):
        msg = f"Unable to find a package named '{package}'!"
        raise ImportError(msg)

    asset = files(package=package).joinpath(filename)
    with as_file(asset) as path:
        if not path.exists():
            msg = f"Asset at path '{path}' does not exist! Is there a file named '{filename}' in the '{package}' package?"
            raise FileNotFoundError(msg)
        return discord.File(fp=path, filename=filename, description=description, spoiler=spoiler)


def title(string: str, /) -> str:
    """Replace any underscores in a string with spaces, then titlecase it.

    Args:
        string: The string to modify.

    Returns:
        The modified string.
    """
    return string.replace("_", " ").title()


class TimestampStyle(StrEnum):
    """Discord timestamp format options."""

    SHORT_TIME = "t"
    """`4:45 PM`"""
    LONG_TIME = "T"
    """`4:45:33 PM`"""
    SHORT_DATE = "d"
    """`7/5/25`"""
    LONG_DATE = "D"
    """`July 5th, 2025`"""
    SHORT_DATE_AND_TIME = "f"
    """`July 5th, 2025 at 4:45 PM`"""
    LONG_DATE_AND_TIME = "F"
    """`Saturday, July 5th, 2025 at 4:45 PM`"""
    RELATIVE = "R"
    """`3 minutes ago`"""


def format_datetime(dt: datetime, style: TimestampStyle = TimestampStyle.SHORT_DATE_AND_TIME) -> str:
    """Format a datetime into a Discord-compatible timestamp string.

    Similar to [`discord.utils.format_dt`][], but uses an enum to provide better code readability.

    Example:
        ```python
        from discord.utils import utcnow
        from tidegear.utils import TimestampStyle, format_datetime

        datetime = utcnow()
        print(format_datetime(dt=datetime, style=TimestampStyle.LONG_DATE_AND_TIME))
        ```

    Args:
        dt: The datetime to convert into a Discord timestamp.
        style: The timestamp style to apply.

    Returns:
        A string like `<t:1618924800:f>` that Discord will render according to the given style.
    """
    return f"<t:{int(dt.timestamp())}:{style}>"


async def send_error(
    messeagable: commands.Context | discord.abc.Messageable,
    /,
    content: str | None = None,
    func: Callable[[str], str] = cf.error,
    **kwargs: Any,
) -> discord.Message:
    """Send a message with the content wrapped in an error function.

    Args:
        messeagable: The channel or context to send the message to.
        content: The content of the message.
        func: The function to use to wrap the message.
        **kwargs: Additional keyword arguments to pass to `await messeagable.send()`.

    Returns:
        The sent message.
    """
    if content:
        content = func(content)
    return await messeagable.send(content=content, **kwargs)
