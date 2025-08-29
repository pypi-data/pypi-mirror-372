# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
# © 2025 cswimr

"""This module contains a subclass of [`commands.Cog`][redbot.core.commands.Cog].
Cogs using this library should inherit from the [`tidegear.Cog`][] class within this module.
"""

import re
from pathlib import Path
from typing import List

import humanize
from discord import Emoji, Guild, HTTPException, Thread, User, abc
from red_commons.logging import RedTraceLogger, getLogger
from redbot.core import commands, data_manager
from redbot.core.bot import Red
from redbot.core.utils import chat_formatting as cf
from typing_extensions import override

from tidegear.metadata import CogMetadata
from tidegear.version import meta

ALLOWED_EMOJI_EXTENSIONS = {"PNG", "WEBP", "JPEG", "JPG", "GIF", "AVIF"}


class Cog(commands.Cog):
    """The base Cog class that cogs using Tidegear should inherit from.

    This class contains a couple of useful utility methods.
    Keep in mind that you **must** have a `meta.json` file in your cog's
    [data folder][redbot.core.data_manager.bundled_data_path] in order to use this cog class.

    Warning:
        Subclasses of this class should not have method names that start with `tidegear_` or `red_`.
        They also should not have dunder methods whose names begin with `__tidegear` or `__red`.
        Methods with these names are reserved for future functionality within Tidegear or Red, respectively.

    Example:
        ```python
        from redbot.core.bot import Red
        from redbot.core import commands
        import tidegear

        class MyCog(tidegear.Cog):
        \"\"\"My first Tidegear cog.\"\"\"

            def __init__(self, bot: Red) -> None:
                super().__init__(bot)

            @commands.command()
            async def hello(self, ctx: commands.Context) -> None:
                await ctx.send(f"Hello from {self.metadata.name}!")
        ```

    Args:
        bot: The bot object passed to the cog during loading.

    Attributes:
        application_emojis: The application emojis you've provided to upload with the cog. Uploads happen during cog loading.
        bot: The bot object passed to the cog during loading.
        bundled_data_path: The cog's bundled data path, retrieved from [`redbot.core.data_manager.bundled_data_path`][] at cog initialization time.
            You should **never** write to this directory from your code,
            as this directory points to the `data` directory within your own cog's source code.
        logger: A logger automatically populated with the name of your cog repository and the cog's actual classname.
        me: A user object representing the bot user.
        metadata: A Python object representing the contents of your cog's `meta.json` file.
        runtime_data_path: The cog's runtime data path, retrieved from [`redbot.core.data_manager.cog_data_path`][] at cog initialization time.
            You can safely write to this directory from your code without issue.

    Raises:
        FileNotFoundError: Raised if this class is loaded as a cog without a`meta.json` file
            being present in the cog's [data folder][redbot.core.data_manager.bundled_data_path].
    """

    def __init__(self, bot: Red) -> None:
        super().__init__()
        self.bot: Red = bot
        # this is fine because Red itself will fail if the client isn't logged in way before this cog would be loaded
        self.me: User = bot.get_user(bot.user.id)  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
        self.bundled_data_path: Path = data_manager.bundled_data_path(self)
        self.runtime_data_path: Path = data_manager.cog_data_path(self)
        meta_path = self.bundled_data_path / "meta.json"
        if not meta_path.exists():
            msg = f"There is no metadata file located at {meta_path}!"
            raise FileNotFoundError(msg)
        self.metadata: CogMetadata = CogMetadata.from_json(self.__cog_name__, meta_path)
        self.logger: RedTraceLogger = getLogger(f"red.{self.metadata.repository.name}.{self.metadata.name}")
        self._internal_logger: RedTraceLogger = self.logger.getChild("tidegear")
        self._application_emoji_path = self.bundled_data_path / "emojis"
        self._application_emoji_prefix: str = self.__cog_name__.lower()
        self.application_emojis: dict[str, Emoji] = {}

    @override
    async def cog_load(self) -> None:
        """Run asynchronous code during the cog loading process.

        Subclasses may override this if they want special asynchronous loading behaviour.
        The `__init__` special method does not allow asynchronous code to run
        inside it, thus this is helpful for setting up code that needs to be asynchronous.

        Danger:
            Please ensure that you call `await super().cog_load()` within your overridden method,
            as this method is implemented within Tidegear's Cog class and is expected to be ran.
        """
        if self.provides_application_emojis:
            self._internal_logger.debug("Application emojis are provided by this cog. Uploading emojis to Discord.")
            await self.add_application_emojis()

    @override
    async def cog_unload(self) -> None:
        """Run asynchronous code during the cog unloading process.

        Danger:
            Please ensure that you call `await super().cog_unload()` within your overridden method,
            as this method may be implemented within Tidegear's Cog class in the future and is expected to be ran.
        """
        pass

    @override
    def format_help_for_context(self, ctx: commands.Context) -> str:
        """Format the help string based on values in context.

        The steps are (currently, roughly) the following:

        - Get the cog class's localized help text.
        - Substitute `[p]` for [`ctx.clean_prefix`][discord.ext.commands.Context.clean_prefix].
        - Substitute `[botname]` for [`ctx.me.display_name`][discord.abc.User.display_name].
        - Add cog metadata from `self.metadata`.

        More steps may be added at a later time.

        Args:
            ctx: The context to substitute values for.

        Returns:
            The resulting help text.
        """
        base = (super().format_help_for_context(ctx) or "").rstrip("\n") + "\n"
        parts: List[str] = [base]
        parts.append(f"{cf.bold('Cog Version:')} [{self.metadata.version}]({self.metadata.repository.url})")
        author_label = "Authors:" if len(self.metadata.authors) >= 2 else "Author:"  # noqa: PLR2004
        parts.append(f"{cf.bold(author_label)} {cf.humanize_list([author.markdown for author in self.metadata.authors])}")
        if self.metadata.documentation is not None:
            parts.append(f"{cf.bold('Documentation:')} {self.metadata.documentation}")
        parts.append(f"{cf.bold('Tidegear Version:')} {meta.markdown}")
        return "\n".join(parts)

    @property
    def provides_application_emojis(self) -> bool:
        """Check whether or not this cog ships with application emojis.

        Returns:
            Whether or not this cog ships with application emojis.
                If this is `True`, Tidegear will automatically upload the provided emojis to Discord upon cog load.
        """
        if not self._application_emoji_path.exists():
            return False
        if not self._application_emoji_path.is_dir():
            return False
        if sum((1 for f in self._application_emoji_path.iterdir() if f.is_file()), start=0) != 0:
            return True
        return False

    def _get_emoji_name(self, name: str) -> str:
        return (self._application_emoji_prefix + "_" + name).replace("-", "_").replace(" ", "_").lower()

    def get_application_emoji(self, name: str) -> Emoji | None:
        """Retrieve an application emoji from its filename.

        Args:
            name: The filename of the emoji you'd like to retrieve. Must originate from this cog.

        Raises:
            NotImplementedError: Raised if [`self.provides_application_emojis`][tidegear.Cog.provides_application_emojis]
                evaluates to `False`, indicating that this cog does not ship with any application emojis to fetch.

        Returns:
            The retrieved emoji matching the provided filename, or `None` if it could not be found.
        """
        if not self.provides_application_emojis:
            msg = f"Cog '{self.__cog_name__}' does not provide application emojis!"
            raise NotImplementedError(msg)
        name = self._get_emoji_name(name)
        return self.application_emojis.get(name, None)

    async def add_application_emojis(self) -> dict[str, Emoji]:
        """Upload all of the application emojis that ship with a cog to Discord.

        This is automatically ran by [`cog_load`][tidegear.Cog.cog_load]
        if your cog [ships with application emojis][tidegear.Cog.provides_application_emojis],
        so you shouldn't usually have to run this yourself.

        Raises:
            NotImplementedError: Raised if [`self.provides_application_emojis`][tidegear.Cog.provides_application_emojis]
                evaluates to `False`, indicating that this cog does not ship with any application emojis to upload.

        Returns:
            A dictionary containing the cog's emojis and their names as keys.
                Consider using [`self.get_application_emoji`][tidegear.Cog.get_application_emoji]
                to access uploaded emojis instead of checking keys manually.
        """
        if not self.provides_application_emojis:
            msg = f"Cog '{self.__cog_name__}' does not provide application emojis!"
            raise NotImplementedError(msg)

        max_emoji_filesize = 256 * 1024  # 256 KB
        regex_pattern = re.compile(r"^[a-zA-Z0-9_]+$")
        emojis: dict[str, Emoji] = {}
        existing_application_emojis = await self.bot.fetch_application_emojis()

        for file in self._application_emoji_path.iterdir():
            if not file.is_file():
                continue

            if (suffix := file.suffix.strip(".").upper()) not in ALLOWED_EMOJI_EXTENSIONS:
                self.logger.error(
                    "Emoji file '%s' has an unsupported extension: '%s'\nSupported extensions: '%s'",
                    file,
                    suffix,
                    cf.humanize_list(items=[cf.inline(extension) for extension in ALLOWED_EMOJI_EXTENSIONS], style="unit"),
                )
                continue

            if (filesize := file.stat().st_size) > max_emoji_filesize:
                self.logger.error(
                    "Emoji file '%s' is too large to be uploaded to Discord! (%s > %s)",
                    file,
                    humanize.naturalsize(filesize),
                    humanize.naturalsize(max_emoji_filesize),
                )
                continue

            emoji_name = self._get_emoji_name(name=file.stem)
            if not regex_pattern.fullmatch(emoji_name):
                self._internal_logger.error("Invalid emoji name '%s'! Emoji names must match regex pattern '%s'.", emoji_name, regex_pattern)
                continue

            emoji_name_length_limit = 32
            if (length := len(emoji_name)) > emoji_name_length_limit:
                self._internal_logger.error(
                    "Skipping application emoji '%s' due to exceeding the name length limit. (%i > %i)", emoji_name, length, emoji_name_length_limit
                )
                continue

            if conflicting_emoji := next((e for e in existing_application_emojis if e.name == emoji_name), None):
                self._internal_logger.verbose("Skipping application emoji '%s', due to conflicting name.", emoji_name)
                emojis[emoji_name] = conflicting_emoji
                continue

            try:
                with open(file, mode="rb") as f:
                    emoji = await self.bot.create_application_emoji(name=emoji_name, image=f.read())
                emojis[emoji_name] = emoji
                existing_application_emojis.append(emoji)
                self._internal_logger.debug("Successfully uploaded application emoji '%s' to Discord.", emoji_name)
            except HTTPException:
                self._internal_logger.exception("Failed to upload application emoji '%s' from file '%s'!", emoji_name, file)
                continue

        self.application_emojis = emojis
        return emojis

    async def delete_application_emojis(self, fetch: bool = False) -> list[Emoji]:
        """Delete all application emojis associated with this cog.

        Args:
            fetch: Whether or not to fetch all application emojis from the Discord API.
                If this is not `True`, the application emoji cache on this cog class will be used instead.

        Returns:
            The application emojis that were deleted.
        """
        if fetch:
            to_delete = await self.bot.fetch_application_emojis()
        else:
            to_delete = self.application_emojis.values()

        deleted_emojis: list[Emoji] = []

        for emoji in to_delete:
            if not emoji.name.startswith(self._application_emoji_prefix):
                continue

            if not emoji.is_application_owned():
                self._internal_logger.warning("Application emoji '%s' with id '%s' does not appear to be an application emoji.", emoji.name, emoji.id)
                continue

            deleted_emojis.append(emoji)
            await emoji.delete()
            self._internal_logger.debug("Deleted application emoji '%s' with id '%s'.", emoji.name, emoji.id)
        return deleted_emojis

    async def get_or_fetch_user(self, user_id: int) -> User:
        """Retrieve a user from the internal cache, or fetch it if it cannot be found.

        Use this sparingly, as the [`fetch_user`][discord.ext.commands.Bot.fetch_user] endpoint has a strict ratelimit.

        Args:
            user_id: The ID of the user to retrieve.

        Returns:
            The retrieved user.
        """
        user = self.bot.get_user(user_id)
        if not user:
            user = await self.bot.fetch_user(user_id)
        return user

    async def get_or_fetch_guild(self, guild_id: int) -> Guild:
        """Retrieve a guild from the internal cache, or fetch it if it cannot be found.

        Use this sparingly, as the [`fetch_guild`][discord.ext.commands.Bot.fetch_guild] endpoint has a strict ratelimit.

        Args:
            guild_id: The ID of the guild to retrieve.

        Returns:
            The retrieved guild.
        """
        guild = self.bot.get_guild(guild_id)
        if not guild:
            guild = await self.bot.fetch_guild(guild_id)
        return guild

    @staticmethod
    async def get_or_fetch_channel(guild: Guild, channel_id: int) -> abc.GuildChannel | Thread:
        """Retrieve a channel or thread from the internal cache, or fetch it if it cannot be found.

        Use this sparingly, as the [`fetch_channel`][discord.Guild.fetch_channel] endpoint has a strict ratelimit.

        Args:
            guild: The guild to use to retrieve the channel.
            channel_id: The ID of the channel to retrieve.

        Returns:
            The retrieved channel or thread.
        """
        channel = guild.get_channel_or_thread(channel_id)
        if not channel:
            channel = await guild.fetch_channel(channel_id)
        return channel
