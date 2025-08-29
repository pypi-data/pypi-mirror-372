# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
# © 2025 cswimr

"""Defines a subclass of `[pydantic.BaseModel`][] for use in Tidegear cogs."""

from typing import Any, Callable, Literal, Self, TypeVar, overload

import orjson
from discord import Colour, Embed
from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, Field
from pydantic.main import IncEx
from pydantic_core import ErrorDetails, ValidationError
from red_commons.logging import RedTraceLogger
from redbot.core import commands
from redbot.core.utils.chat_formatting import bold, error, inline
from redbot.core.utils.views import _ACCEPTABLE_PAGE_TYPES, SimpleMenu
from typing_extensions import override

from tidegear import Cog
from tidegear.metadata import CogMetadata

R = TypeVar("R")


class BaseModel(PydanticBaseModel):
    """A subclass of [`pydantic.BaseModel`][] that adds some useful helper methods."""

    model_config = ConfigDict(validate_assignment=True, arbitrary_types_allowed=True)

    @overload
    @classmethod
    def validate_field(cls, field_name: str, field_value: Any, converter: Callable[[Any], R]) -> R: ...

    @overload
    @classmethod
    def validate_field(cls, field_name: str, field_value: Any, converter: None = None) -> Any: ...

    @classmethod
    def validate_field(cls, field_name: str, field_value: Any, converter: Callable[[Any], R] | None = None) -> R | Any:
        """Validate a single field without running validation for an entire model. Wraps internal Pydantic methods to do this.

        Args:
            field_name: The name of the field to validate your input against.
            field_value: The input value to validate.
            converter: A function to use to convert the resulting value.

        Returns:
            The validated input value.

        """
        model: Self = cls.__pydantic_validator__.validate_assignment(cls.model_construct(), field_name, field_value)  # pyright: ignore[reportAssignmentType]
        attribute = getattr(model, field_name)
        if converter:
            return converter(attribute)
        return attribute

    @overload
    def json(
        self,
        /,
        *,
        include: IncEx = ...,
        exclude: IncEx = ...,
        remove_token: bool = ...,
        string: Literal[False] = False,
        encoding: str = ...,
        indent: bool = ...,
    ) -> dict[str, Any]: ...

    @overload
    def json(
        self,
        /,
        *,
        include: IncEx = ...,
        exclude: IncEx = ...,
        remove_token: bool = ...,
        string: Literal[True],
        encoding: str = ...,
        indent: bool = ...,
    ) -> str: ...

    @override
    def json(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        /,
        *,
        include: IncEx = set(),
        exclude: IncEx = set(),
        remove_token: bool = True,
        string: bool = False,
        encoding: str = "utf-8",
        indent: bool = False,
    ) -> dict[str, Any] | str:
        """Dump the contents of the model to a JSON-serializable dictionary.

        Set an attribute's default value to `Field(exclude=True)` to exclude it from this function's output automatically.

        Args:
            include: A set of fields to include in the model dump.
            exclude: A set of fields to exclude from the model dump.
            remove_token: Whether or not to recursively remove keys named `token` from the output object.
            string: Whether or not to use `orjson.dumps()` to convert the resulting dictionary to a string.
            encoding: The encoding to use to decode the bytes returned by `orjson.dumps()`.
            indent: Whether or not to pretty-print the output. This is slower and should only be used when an end user is seeing the output.

        Returns:
            (dict[str, Any]): A Dictionary containing only JSON-serializable attributes, if `string` is `False`.
            (str): A string representation of the Dictionary mentioned previously, converted using `orjson.dumps()`.

        """
        params = {"exclude": exclude, "mode": "json"}
        if include:
            params["include"] = include

        obj = self.model_dump(**params)

        if remove_token:
            obj = self._recurse_modify(obj, "token", lambda token: "*" * 6 if token else None)

        if string:
            opts: int | None = None
            if indent:
                opts = orjson.OPT_INDENT_2
            return orjson.dumps(obj, option=opts).decode(encoding)

        return obj

    def _recurse_modify(self, obj: Any, key: str, modify_fn: Callable[..., Any]) -> Any:
        """Return a deep-copied version of obj where every dict-key matching `key` has its value replaced by modify_fn(old_value)."""
        if isinstance(obj, dict):
            new_dict = {}
            for k, v in obj.items():
                if k == key:
                    new_dict[k] = modify_fn(v)
                else:
                    new_dict[k] = self._recurse_modify(v, key, modify_fn)
            return new_dict
        if isinstance(obj, list):
            return [self._recurse_modify(item, key, modify_fn) for item in obj]
        if isinstance(obj, tuple):
            return tuple(self._recurse_modify(item, key, modify_fn) for item in obj)
        if isinstance(obj, set):
            return {self._recurse_modify(item, key, modify_fn) for item in obj}
        return obj

    @staticmethod
    def _custom_validation_messages() -> dict[str, str | dict[str, str]]:
        return {
            "string_pattern_mismatch": {
                r"^[\w\-]+$": "String may only contain letters, numbers, underscores, and hyphens.",
            },
        }

    @classmethod
    def _replace_error_messages(cls, validation_error: ValidationError, /) -> list[ErrorDetails]:
        """Replace a few error messages with more human-readable variants.

        Args:
            validation_error: The Pydantic ValidationError to convert the messages of.

        Raises:
            ValueError:
            TypeError:

        Returns:
            The converted messages.
        """
        new_errors: list[ErrorDetails] = []
        for err in validation_error.errors():
            err_type = err.get("type")
            custom_message = cls._custom_validation_messages().get(err_type)

            if err_type == "string_pattern_mismatch":
                if not isinstance(custom_message, dict):
                    msg = f"Invalid type for {err_type}!"
                    raise TypeError(msg)

                if not (ctx := err.get("ctx")) or not (pattern := ctx.get("pattern")):
                    msg = "Error details do not contain a regex pattern!"
                    raise ValueError(msg)

                for k, v in custom_message.items():
                    if pattern == k:
                        err["msg"] = v.format(**ctx)

            elif isinstance(custom_message, str):
                ctx = err.get("ctx")
                err["msg"] = custom_message.format(**ctx) if ctx else custom_message

            new_errors.append(err)
        return new_errors

    @classmethod
    async def validation_error_menu(
        cls,
        err: ValidationError,
        ctx: commands.Context | None = None,
        *,
        class_name: str | None = None,
        metadata: CogMetadata | None = None,
        logger: RedTraceLogger | None = None,
        title: str = "🚫 Validation Error",
        color: Colour | int = Colour.red(),
        per_page: int = 5,
    ) -> SimpleMenu | None:
        """Take a Pydantic [`ValidationError`][pydantic_core.ValidationError],
        split its [`.errors()`][pydantic_core.ValidationError.errors] into pages,
        and create a SimpleMenu from them.

        Example:
            ```python
            from typing import Annotated
            from pydantic import StringConstraints, ValidationError
            from tidegear.pydantic import BaseModel


            class ExampleModel(BaseModel):
                string: Annotated[str, StringConstraints(min_length=3)]


            try:
                ExampleModel(string="hi")
            except ValidationError as err:  # String should have at least 3 characters (string_too_short)
                if menu := await ExampleModel.validation_error_menu(err, ctx):
                    await menu.start(ctx)
            ```

        Args:
            err: The ValidationError to create an error embed from.
            ctx: The context to use to provide additional help when the error occurred within a command.
            class_name: The name of the class to show in the resulting embed's description.
                This only needs to be provided if the class you're validating against doesn't inherit from [`BaseModel`][tidegear.pydantic.BaseModel].
            metadata: Cog metadata to use to populate the resulting embed.
            logger: A logger to log the exception to.
            title: The title of the created embeds.
            color: The color of the created embeds.
            per_page: How many validation errors to list per page.

        Returns:
            (SimpleMenu): The created SimpleMenu, which you can then start with
                [`await SimpleMenu.start(ctx)`][redbot.core.utils.views.SimpleMenu.start].
            (None): If `ctx` is provided and the bot cannot post embeds in the context channel,
                or if the [`ValidationError`][pydantic_core.ValidationError] exception doesn't provide any errors.

        """
        lines: list[str | None] = [
            f"Validation error encountered for the {inline(class_name or err.title)} class!",
            (f"Please check {inline(f'{ctx.clean_prefix}help {ctx.command.qualified_name}')} to ensure you are passing the correct arguments.")
            if (ctx and ctx.command)
            else None,
            f"If this is unexpected or you're having trouble working around this error, please report it [here]({metadata.repository.issues})."
            if metadata
            else None,
        ]
        description = "\n".join(line for line in lines if line is not None)

        if logger:
            logger.error(lines[0], exc_info=err)

        if ctx:
            if not await ctx.embed_requested():
                await ctx.send(
                    f"{error('Tried to post an issue embed, but I cannot post embeds in this channel or embeds are disabled!')}\n\n{description}"
                )
                return None

        problems = cls._replace_error_messages(err)
        total = len(problems)
        if total == 0:
            return None

        footer_text = ""

        if tb := err.__traceback__:
            module = tb.tb_frame.f_globals.get("__name__", "unknown")
            line = tb.tb_lineno
            function = tb.tb_frame.f_code.co_name
            footer_text = f"• Exception in module '{module}' in function '{function}' at line #{line}\n"

        pages: list[_ACCEPTABLE_PAGE_TYPES] = []
        total_pages = (total - 1) // per_page + 1

        for i in range(0, total, per_page):
            embed = Embed(title=title, color=color, description=description)
            embed.set_footer(text=footer_text + f"• Page {i // per_page + 1}/{total_pages}")

            for problem in problems[i : i + per_page]:
                loc = ".".join(str(x) for x in problem["loc"])
                msg: str = problem.get("msg", "").replace("'", "`")
                input_value = problem.get("input", "UNKNOWN")

                if code := problem.get("type", ""):
                    if code_url := problem.get("url"):
                        code = f"[{inline(code)}]({code_url})"
                else:
                    code = "UNKNOWN"

                field_value = f"{bold('Message:')} {msg}\n{bold('Input: ')} {inline(input_value)}\n{bold('Code:')} {code}"
                embed.add_field(name=f"Field: {inline(loc or 'base')}", value=field_value, inline=False)

            pages.append(embed)

        return SimpleMenu(pages)


class CogModel(BaseModel):
    """Wrapper around [`BaseModel`][tidegear.pydantic.BaseModel] that adds a `cog` attribute.

    Attributes:
        cog: The cog that instantiated this model.
    """

    cog: Cog = Field(exclude=True)
