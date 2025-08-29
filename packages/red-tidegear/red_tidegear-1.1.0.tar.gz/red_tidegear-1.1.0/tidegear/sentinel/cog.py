# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
# © 2025 cswimr

"""Cog class for cogs using the Sentinel moderation system."""

import inspect
import logging as py_logging
import pathlib
from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Any, Literal, Mapping

from class_registry.base import RegistryKeyError
from class_registry.registry import ClassRegistry
from discord import Color, Embed, Forbidden, Guild, Interaction, Member, Message, NotFound, Permissions, Thread, User, abc
from discord.abc import MISSING
from discord.ext import tasks
from discord.utils import utcnow
from piccolo.columns import Or, Where
from piccolo.engine.sqlite import SQLiteEngine
from red_commons import logging
from redbot.core import Config, app_commands, commands
from redbot.core.bot import Red
from redbot.core.data_manager import cog_data_path
from redbot.core.utils import chat_formatting as cf
from redbot.core.utils.views import _ACCEPTABLE_PAGE_TYPES, SimpleMenu
from redbot_orm.sqlite import register_cog
from typing_extensions import override

from tidegear import Cog
from tidegear.exceptions import ConfigurationError
from tidegear.sentinel.db import Change, Moderation, PartialChannel, PartialGuild, PartialUser
from tidegear.sentinel.type import ModerationType, moderation_type_registry
from tidegear.utils import TimestampStyle, class_overrides_method, format_datetime, get_asset_as_file, send_error, set_env, title


class SentinelCog(Cog):
    """The base cog class for cogs that utilize the Sentinel moderation system.

    Keep in mind that you **must** have a `meta.json` file in your cog's
    [data folder][redbot.core.data_manager.bundled_data_path] in order to use this cog class.

    Warning:
        Subclasses of this class should not have method names that start with `sentinel`, `tidegear_`, or `red_`.
        They also should not have dunder methods whose names begin with `__sentinel`, `__tidegear`, or `__red`.
        Methods with these names are reserved for future functionality within Sentinel, Tidegear, or Red, respectively.

    Args:
        bot: The bot object passed to the cog during loading.

    Attributes:
        moderation_type_registry: The registry for moderation types that you can access
            to retrieve [`ModerationType`][tidegear.sentinel.ModerationType] objects.
        moderation_types: A list of your cog's moderation types. You should be overriding this in `__init__()`.
        db: The database engine.
        sentinel_config: The global Sentinel configuration.
    """

    _sentinel_expiry_loop: tasks.Loop | None = None

    def __init__(self, bot: Red) -> None:
        super().__init__(bot)
        self.moderation_type_registry: ClassRegistry[ModerationType] = moderation_type_registry
        self.db: SQLiteEngine = MISSING
        self._db_path: pathlib.Path = cog_data_path(raw_name="TidegearSentinel")
        self.sentinel_config: Config = Config.get_conf(
            cog_instance=None, identifier=294518358420750336, cog_name="TidegearSentinel", force_registration=True
        )
        self._sentinel_logger: logging.RedTraceLogger = self.logger.getChild("sentinel")
        self._sentinel_register_config()

        # If we don't override aiosqlite's logging level, it will spam the console with dozens of debug messages per query.
        # This is unnecessary because the information that aiosqlite logs is not particularly useful to the bot owner.
        # This is a subpar solution though as it overrides it for any other cogs that are using aiosqlite too.
        # If there's a better solution that you're aware of, please let me know in Discord or in a CoastalCommits issue.
        if self.logger.level >= logging.VERBOSE or self.logger.level == py_logging.NOTSET:
            py_logging.getLogger("aiosqlite").setLevel(py_logging.INFO)
        elif self.logger.level < logging.VERBOSE:
            py_logging.getLogger("aiosqlite").setLevel(self.logger.level)

    @override
    async def cog_load(self) -> None:
        """Run asynchronous code during the cog loading process.

        Subclasses may override this if they want special asynchronous loading behaviour.
        The `__init__` special method does not allow asynchronous code to run
        inside it, thus this is helpful for setting up code that needs to be asynchronous.

        Danger:
            Please ensure that you call `await super().cog_load()` within your overridden method,
            as this method sets up the database engine and moderation type registry for Sentinel cogs.

        """
        await super().cog_load()
        self._sentinel_logger.verbose("Using the following path to store the Sentinel SQLite database: %s", self._db_path)
        with set_env(key="PICCOLO_CONF", value="tidegear.sentinel.db.piccolo_conf", logger=self._sentinel_logger):
            self.db = await register_cog(
                cog_instance=self._db_path, tables=[Change, Moderation, PartialChannel, PartialGuild, PartialUser], trace=True
            )

        for moderation_type in self.moderation_types:
            if moderation_type.key in self.moderation_type_registry:
                conflict = self.moderation_type_registry[moderation_type.key]
                cls = conflict.__class__
                mod_name = cls.__module__
                file_path = inspect.getfile(cls)
                self._sentinel_logger.error(
                    "Cannot add moderation type with duplicate key '%s'! Conflicting type: '%s' (class name: '%s', module: '%s', file: '%s')",
                    moderation_type.key,
                    conflict.key,
                    cls.__qualname__,
                    mod_name,
                    file_path,
                )
                continue
            self.moderation_type_registry.register(key=moderation_type.key)(moderation_type)
            self._sentinel_logger.verbose("Registered moderation type with key '%s'", moderation_type.key)

        self._sentinel_monitor_expiry_loop.start()

    @override
    async def cog_unload(self) -> None:
        """Run asynchronous code during the cog unloading process.

        Danger:
            Please ensure that you call `await super().cog_unload()` within your overridden method,
            as this method cleans up the Sentinel expiry loop and moderation type registry, and must be ran.
        """
        await super().cog_unload()
        for moderation_type in self.moderation_types:
            if moderation_type.key not in self.moderation_type_registry:
                self._sentinel_logger.warning(
                    "Moderation type with key '%s' does not exist in the type registry, skipping unregistration.", moderation_type.key
                )
                continue
            self.moderation_type_registry.unregister(key=moderation_type.key)
            self._sentinel_logger.trace("Unregistered moderation type with key '%s'", moderation_type.key)

        if SentinelCog._sentinel_expiry_loop and SentinelCog._sentinel_expiry_loop.is_running:
            SentinelCog._sentinel_expiry_loop.cancel()
            self._sentinel_logger.debug("Cancelled expiry loop!")

    @override
    async def red_delete_data_for_user(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        *,
        requester: Literal["discord_deleted_user", "owner", "user", "user_strict"],
        user_id: int,
    ) -> None:
        async def anonymize_user(user_id: int, /, *, deleted: bool) -> None:
            for user in await PartialUser.objects().where(PartialUser.user_id == user_id):
                await user.update_self(values={PartialUser.last_known_name: "deleted_user" if deleted else "unknown"})

        match requester:
            case "discord_deleted_user":
                await self.sentinel_config.user_from_id(user_id).clear()
                await anonymize_user(user_id, deleted=True)
            case "owner" | "user_strict":
                await self.sentinel_config.user_from_id(user_id).clear()
                await anonymize_user(user_id, deleted=False)
            case "user":
                await self.sentinel_config.user_from_id(user_id).clear()
            case _:
                self._sentinel_logger.warning("Invalid requester passed to red_delete_data_for_user: %s", requester)

    def _sentinel_register_config(self) -> None:
        self.sentinel_config.register_guild(
            show_moderator=True,
            use_discord_permissions=True,
            respect_hierarchy=True,
            dm_users=True,
            log_channel=None,
            immune_roles=[],
            auto_evidenceformat=False,
        )

        moderation_type = {
            "show_in_history": True,
            "show_moderator": None,
            "use_discord_permissions": None,
            "dm_users": None,
        }

        self.sentinel_config.init_custom(group_identifier="types", identifier_count=2)
        self.sentinel_config.register_custom(group_identifier="types", **moderation_type)

    @property
    def moderation_types(self) -> list[type[ModerationType]]:
        """Return a set of moderation types that are added by this cog.

        If you are adding any custom moderation types, you **must** override this method to return your new moderation types.
        If you do not do this, then your types will never be added to the type registry.

        Example:
            ```python
            from sentinel.tidegear import ModerationType
            from .types import Warn, Mute, Tempban, Ban


            @property
            def moderation_types(self) -> list[type[ModerationType]]:
                return [Warn, Mute, Tempban, Ban]  # Do not create instances of these classes! Just provide their types.
            ```
        """
        return []

    @property
    def adds_moderation_types(self) -> bool:
        """Check whether or not a cog class overrides the [`moderation_types`][tidegear.sentinel.SentinelCog.moderation_types] method."""
        return class_overrides_method(child=type(self), parent=SentinelCog, method_name="moderation_types")

    def get_sentinel_cogs(self) -> Mapping[str, "SentinelCog"]:
        """Get a mapping of all cogs that are currently loaded that are subclasses of SentinelCog.

        Tip:
            This includes the cog instance executing this method!

        Returns:
            A mapping of cog names to SentinelCog instances.
        """
        return {name: cog for name, cog in self.bot.cogs.items() if isinstance(cog, SentinelCog)}

    async def log_channel(self, guild: Guild) -> abc.GuildChannel | Thread | None:
        """Retrieve the moderation logging channel for a guild.

        Args:
            guild: The guild to fetch the logging channel for.

        Returns:
            The fetched channel.
        """
        channel_id = await self.sentinel_config.guild(guild).log_channel()
        if channel_id is None:
            return None

        try:
            channel = await self.get_or_fetch_channel(guild, channel_id)
            self._sentinel_logger.trace("channel: %s, channel type: %s", channel, type(channel))
            return channel
        except NotFound:
            return None

    async def moderate(
        self,
        ctx: commands.Context | Interaction,
        target: Member | User | abc.GuildChannel | Thread,
        moderation_type: ModerationType | str,
        silent: bool = False,
        **kwargs: Any,
    ) -> None | Moderation:
        """Moderate a user.

        Checks if the target can be moderated, then calls the handler method of the moderation type specified.

        Args:
            ctx: The context of the command.
                If this is a [`discord.Interaction`][] object, it will be converted to a [`commands.Context`][redbot.core.commands.Context] object.
                Additionally, if the interaction originated from a context menu, the [`ctx.author`][discord.ext.commands.Context.author] attribute
                will be overridden to [`interaction.user`][discord.Interaction.user].
            target: The target user or channel to moderate.
            moderation_type: The moderation type (handler) to use.
            silent: Whether or not to message the target.
            **kwargs: Any additional keyword arguments to pass to the handler method.

        Returns:
            The resulting Moderation, or `None` if an error was encountered.
        """
        if isinstance(moderation_type, str):
            moderation_type = moderation_type_registry[moderation_type.lower()]

        if isinstance(ctx, Interaction):
            interaction = ctx
            ctx = await commands.Context.from_interaction(interaction)
            if isinstance(interaction.command, app_commands.ContextMenu):
                ctx.author = interaction.user

        if not ctx.guild:
            await send_error(ctx, content="Cannot moderate users outside of a guild!", ephemeral=True)
            return None

        try:
            await self.check_moddable(target=target, ctx=ctx, moderation_type=moderation_type)
        except (PermissionError, ValueError) as err:
            await send_error(ctx, content=str(err), ephemeral=True)
            return None

        moderation = await moderation_type.handler(target=target)(ctx=ctx, target=target, **kwargs)

        if not silent:
            try:
                await self.contact_target(moderation)
            except (ConfigurationError, TypeError) as err:
                self.logger.warning("Unable to contact target '%s'!", target.id, exc_info=err)
            except Forbidden:
                pass

        try:
            await self.send_log(moderation)
        except ConfigurationError:
            pass

        return moderation

    def check_permissions(
        self,
        user: Member | abc.User | PartialUser,
        required_permissions: Permissions,
        guild: Guild,
        channel: abc.GuildChannel | Thread | None = None,
    ) -> None:
        """Check if a user has a specific permission (or a list of permissions) in a channel.

        Users with the `Administrator` permission will always pass this check.
        An exception will always be raised if the permissions check fails.

        Args:
            user: The user to check the permissions of.
            required_permissions: The permissions to check for.
            guild: The guild to use to retrieve the `user` if it isn't already a [`discord.Member`][] object.
            channel: The guild channel or thread to perform the check in.
                If this is provided, this method will use the [`GuildChannel.permissions_for`][discord.abc.GuildChannel.permissions_for] method,
                which is much more accurate than the [`Member.guild_permissions`][discord.Member.guild_permissions]
                attribute that is used when `channel` isn't provided.

        Raises:
            TypeError: Raised if `user` does not match this method's typehints.
            PermissionError: Raised if the permissions check fails. These error messages are safe to send to end users.
        """
        if isinstance(user, Member):
            member = user
        elif isinstance(user, abc.User):
            member = guild.get_member(user.id)
        elif isinstance(user, PartialUser):
            member = guild.get_member(user.discord_id)
        else:
            msg = "Unsupported type!"
            raise TypeError(msg)

        resolved_permissions = None

        if channel and member:
            resolved_permissions = channel.permissions_for(member)

        elif member:
            resolved_permissions = member.guild_permissions

        if not member or not resolved_permissions:
            msg = f"Could not check permissions for {user.mention}!"
            raise PermissionError(msg)

        if resolved_permissions.administrator:
            return

        if not resolved_permissions >= required_permissions:
            missing = [name for name, wanted in required_permissions if wanted and not getattr(resolved_permissions, name)]
            self._sentinel_logger.trace(
                (
                    "Permissions check failed for user with id '%s' in channel '%s' (guild '%s')\n"
                    "Resolved permissions: %s\nRequired permissions: %s\nMissing: %s"
                ),
                member.id,
                channel.id if channel else None,
                guild.id,
                [name for name, has in resolved_permissions if has],
                [name for name, wanted in required_permissions if wanted],
                missing,
            )

            perms_list = cf.humanize_list([cf.inline(perm) for perm in missing])
            who = "I" if self.me.id == member.id else "You"
            within_channel = f" within the {channel.mention} channel" if channel else ""
            part = f"permissions{within_channel}, which are" if len(missing) > 1 else f"permission{within_channel}, which is"

            msg = f"{who} do not have the {perms_list} {part} required for this action."
            raise PermissionError(msg)

    async def check_moddable(
        self,
        ctx: commands.Context,
        target: User | Member | abc.GuildChannel | Thread,
        moderation_type: ModerationType,
    ) -> None:
        """Check if the `ctx.author` can moderate the target.

        Abstract: Order of Operations:
            - Ensure that the passed context object originates from a guild and that the bot is a member of the guild.
            - Check the bot's permissions against [`moderation_type.permissions`][tidegear.sentinel.ModerationType].
            - If `use_discord_permissions` is `True` in the Sentinel guild configuration,
                check the `ctx.author`'s permissions against [`moderation_type.permissions`][tidegear.sentinel.ModerationType].
            - If the target is a guild member:
                - Ensure that the `ctx.author` is not attempting to moderate themselves.
                - If the `ctx.author` does not have the `Administrator` permission, ensure that the target is not a bot.
                - Ensure that the target does not have the `Administrator` permission.
                - Ensure that the target does not have a role higher than or equal to the bot's top role.
                - If `respect_hierarchy` is `True` in the Sentinel guild configuration,
                    ensure the target does not have a role higher than or equal to the `ctx.author`'s top role.
                - If the `ctx.author` does not have the `Administrator` permission, ensure that the target
                    does not have any of the roles set as immune roles within the Sentinel guild configuration.

        Args:
            ctx: The context where the moderation is taking place.
            target: The target of the moderation.
            moderation_type: The type of the moderation you're wanting to perform.
                Used for checking Red's configuration and confirming that the `ctx.author` and the bot have all of the required permissions.

        Raises:
            ValueError: Raised when `ctx` is outside of a guild context, or the bot user is not in the guild that the passed context originates from.
            PermissionError: Raised if the target cannot be moderated by the `ctx.author`. These error messages are safe to send to end users.
        """
        if not ctx.guild or not isinstance(ctx.channel, (abc.GuildChannel, Thread)):
            msg = "check_moddable is not usable outside of a guild context!"
            raise ValueError(msg)

        if not (me := ctx.guild.get_member(ctx.me.id)):
            msg = "The bot user is not in the guild that the passed Context originates from!"
            raise ValueError(msg)

        is_channel = isinstance(target, (abc.GuildChannel, Thread))

        self.check_permissions(
            user=me, required_permissions=moderation_type.permissions, guild=ctx.guild, channel=target if is_channel else ctx.channel
        )

        use_discord_permissions = await self.sentinel_config.custom(
            "types",
            str(ctx.guild.id),
            moderation_type.key,
        ).use_discord_permissions()

        if use_discord_permissions is None:
            use_discord_permissions = await self.sentinel_config.guild(ctx.guild).use_discord_permissions()

        if use_discord_permissions is True:
            self.check_permissions(
                user=ctx.author, required_permissions=moderation_type.permissions, guild=ctx.guild, channel=target if is_channel else ctx.channel
            )

        if isinstance(target, Member) and isinstance(ctx.author, Member):
            is_moderator_admin = ctx.author.guild_permissions.administrator

            if ctx.author.id == target.id:
                msg = "You cannot moderate yourself!"
                raise PermissionError(msg)

            if not is_moderator_admin and target.bot:
                msg = "You cannot moderate bots!"
                raise PermissionError(msg)

            if target.guild_permissions.administrator:
                msg = "You cannot moderate members with the Administrator permission!"
                raise PermissionError(msg)

            if me.top_role <= target.top_role:
                msg = "You cannot moderate members with a role higher than the bot!"
                raise PermissionError(msg)

            if ctx.author.top_role <= target.top_role and await self.sentinel_config.guild(ctx.guild).respect_hierarchy() is True:
                msg = "You cannot moderate members with a higher role than you!"
                raise PermissionError(msg)

            if not is_moderator_admin:
                immune_roles = await self.sentinel_config.guild(target.guild).immune_roles()
                matching = [role.mention for role in target.roles if role.id in immune_roles]

                if matching:
                    formatted = cf.humanize_list(matching, style="or")
                    plural = "s" if len(matching) > 1 else ""
                    part = "they are" if len(matching) > 1 else "it is an"
                    msg = f"You cannot moderate members with the {formatted} role{plural}, because {part} immune role{plural}!"
                    raise PermissionError(msg)

    async def contact_target(
        self,
        moderation: Moderation,
        *,
        response: Message | None = None,
        case: bool = True,
    ) -> Message:
        """Contact the target user of a moderation with details regarding their case.

        Additionally to the exceptions in the `Raises:` section below, this method can raise all exceptions that [`discord.User.send`][] can.

        Args:
            moderation: The moderation to generate details from.
            response: The response message.
            case: Whether the message is for a moderation case.

        Raises:
            TypeError: Raised when the moderation's target is not a [`PartialUser`][tidegear.sentinel.db.PartialUser].
            ConfigurationError: Raised when the Sentinel configuration disallows sending messages to targeted users.

        Returns:
            The sent message object.
        """
        target = await moderation.target()
        if not isinstance(target, PartialUser):
            msg = f"Cannot message {type(target)}s!"
            raise TypeError(msg)

        moderator = await moderation.moderator()
        guild = await (await moderation.guild()).fetch(bot=self.bot)
        target = await target.fetch(fetcher=guild)

        if channel := next((ch for ch in guild.channels if isinstance(ch, abc.Messageable)), None):
            color = await self.bot.get_embed_color(location=channel)
        else:
            color = Color.red()

        dm_users = await self.sentinel_config.custom("types", str(guild.id), moderation.type.key).dm_users()
        if dm_users is None:
            dm_users = await self.sentinel_config.guild(guild=guild).dm_users()
        if not dm_users:
            msg = "Contacting moderation targets is disabled!"
            raise ConfigurationError(msg)

        if response is not None and not moderation.type.removes_from_guild:
            guild_name = f"[{guild.name}]({response.jump_url})"
        else:
            guild_name = guild.name

        if moderation.duration:
            embed_duration = f" for {cf.humanize_timedelta(timedelta=moderation.duration)}"
        else:
            embed_duration = ""

        embed = Embed(
            title=str.title(moderation.type.verb),
            color=color,
            description=f"You have {moderation.type.embed_desc}{moderation.type.verb}{embed_duration} in {guild_name}.",
            timestamp=moderation.timestamp,
        )

        show_moderator = await self.sentinel_config.custom("types", str(guild.id), moderation.type.key).show_moderator()
        if show_moderator is None:
            show_moderator = await self.sentinel_config.guild(guild).show_moderator()

        if show_moderator and moderator is not None:
            embed.add_field(name="Moderator", value=f"`{moderator.name} ({moderator.user_id})`", inline=False)

        embed.add_field(name="Reason", value=f"`{moderation.reason}`", inline=False)

        if guild.icon:
            embed.set_author(name=guild.name, icon_url=guild.icon.url)
        else:
            embed.set_author(name=guild.name)

        kwargs: dict[str, Any] = {}

        if case:
            embed.set_footer(
                text=f"Case #{moderation.id:,}",
                icon_url="attachment://arrow.png",
            )

            kwargs["file"] = get_asset_as_file(filename="arrow.png", description="Arrow")

        return await target.send(embed=embed, **kwargs)

    async def send_log(self, moderation: Moderation) -> Message:
        """Send a moderation log to a guild's configured moderation channel.

        Args:
            moderation: The moderation to create a log for.

        Raises:
            ConfigurationError: If the moderation's guild has no logging channel configured.

        Returns:
            The resulting logging message.
        """
        guild = await (await moderation.guild()).fetch(self.bot)
        if not (log_channel := await self.log_channel(guild)) or not isinstance(log_channel, abc.Messageable):
            msg = "Logging is disabled!"
            raise ConfigurationError(msg)
        embed = await self.case_embed(moderation, color=await self.bot.get_embed_color(location=log_channel))
        return await log_channel.send(embed=embed)

    @staticmethod
    def is_in_guild(partial_object: PartialChannel | PartialUser, guild: Guild) -> bool:
        if isinstance(partial_object, PartialChannel):
            return bool(guild.get_channel_or_thread(partial_object.channel_id))
        if isinstance(partial_object, PartialUser):
            return bool(guild.get_member(partial_object.user_id))
        msg = f"{partial_object!r} is not a supported type! Got: {type(partial_object)!r}"
        raise TypeError(msg)

    async def case_embed(self, moderation: Moderation, color: Color | None = None) -> Embed:
        """Create a case embed from a Moderation object.

        Args:
            moderation: The moderation object.
            color: The color to use for the embed. Defaults to `Color.red()`.

        Returns:
            The resulting embed containing information from the moderation.
        """
        target = await moderation.target()
        moderator = await moderation.moderator()
        guild = await (await moderation.guild()).fetch(self.bot)

        try:
            if isinstance(target, PartialChannel):
                target = await PartialChannel.upsert(channel=await self.get_or_fetch_channel(guild, channel_id=target.channel_id))
            elif isinstance(target, PartialUser):
                target = await PartialUser.upsert(user=await self.get_or_fetch_user(user_id=target.user_id))
            moderator = await PartialUser.upsert(user=await self.get_or_fetch_user(user_id=moderator.user_id))
        except Exception:
            pass

        target_in_guild = self.is_in_guild(target, guild)
        moderator_in_guild = self.is_in_guild(moderator, guild)

        moderation_type = moderation.type_key
        try:
            moderation_type = moderation.type.name
        except RegistryKeyError:
            pass

        embed = Embed(
            title=f"📕 Case #{moderation.id:,}",
            color=color or Color.red(),
        )

        embed.description = (
            f"{cf.bold('Type:')} {title(moderation_type)}\n"
            f"{cf.bold('Target:')} {target.mention if target_in_guild else cf.inline(text=target.name)} ({cf.inline(text=str(target.discord_id))})\n"
            f"{cf.bold('Moderator:')} {moderator.mention if moderator_in_guild else cf.inline(text=moderator.name)} "
            f"({cf.inline(text=str(moderator.discord_id))})\n"
            f"{cf.bold('Timestamp:')} {format_datetime(dt=moderation.timestamp)} "
            f"| {format_datetime(dt=moderation.timestamp, style=TimestampStyle.RELATIVE)}"
        )

        if moderation.end_timestamp:
            duration_embed = (
                (
                    f"{cf.humanize_timedelta(timedelta=moderation.duration)} "
                    f"| {format_datetime(dt=moderation.timestamp, style=TimestampStyle.RELATIVE)}"
                )
                if not moderation.expired
                else str(cf.humanize_timedelta(timedelta=moderation.duration))
            )
            embed.description += f"\n{cf.bold('Duration:')} {duration_embed}\n{cf.bold('Expired:')} {moderation.expired}"

        if moderation.meta:
            for key, value in moderation.meta.items():
                match key:
                    case "imported_timestamp":
                        timestamp = datetime.fromisoformat(value)
                        embed.description += f"\n{cf.bold(f'{title(key)}:')} {format_datetime(dt=timestamp)}"
                    case _:
                        embed.description += f"\n{cf.bold(f'{title(key)}:')} {value}"

        if moderation.reason:
            embed.add_field(name="Reason", value=cf.box(moderation.reason), inline=False)

        if moderation.resolved:
            try:
                resolver = await moderation.resolver()
                if embed.title:
                    embed.title += " Resolved"
                embed.add_field(
                    name="Resolve Reason",
                    value=f"Resolved by {resolver.mention} ({resolver.id}) for:\n" + cf.box(moderation.resolve_reason),
                    inline=False,
                )
            except ValueError:
                pass
        return embed

    async def changes_menu(self, moderation: Moderation, color: Color | None = None) -> SimpleMenu:
        """Create a menu containing all of the historical changes to a Moderation.

        Args:
            moderation: The moderation to list the changes of.
            color: The color of the resulting embeds within the menu.

        Returns:
            The created SimpleMenu, which you can then start with [`await SimpleMenu.start(ctx)`][redbot.core.utils.views.SimpleMenu.start].
        """
        changes = await moderation.changes()
        guild = await (await moderation.guild()).fetch(self.bot)

        pages: list[_ACCEPTABLE_PAGE_TYPES] = []
        if not changes:
            pages.append("No changes have been made to this case!")
            return SimpleMenu(pages)

        fields_per_embed = 10
        for i in range(0, len(changes), fields_per_embed):
            embed = Embed(
                title=f"📕 Case #{moderation.id:,} Changes",
                color=color or Color.blue(),
            )
            embed.set_footer(text=f"Page {i // fields_per_embed + 1}/{len(changes) // fields_per_embed + 1}")

            for change in changes[i : i + fields_per_embed]:
                moderator = await change.moderator()
                mod_in_guild = self.is_in_guild(moderator, guild)

                change_str = [
                    (
                        f"{cf.bold('Moderator:')} {moderator.mention if mod_in_guild else cf.inline(text=moderator.name)} "
                        f"({cf.inline(text=str(moderator.discord_id))})"
                    ),
                    f"{cf.bold('Reason:')} {change.reason}" if change.reason else "",
                    f"{cf.bold('Duration:')} {cf.humanize_timedelta(timedelta=change.duration)}" if change.duration else "",
                    (
                        f"{cf.bold('End Timestamp:')} {format_datetime(dt=change.end_timestamp)} "
                        f"| {format_datetime(dt=change.timestamp, style=TimestampStyle.RELATIVE)}"
                    )
                    if change.end_timestamp
                    else "",
                    f"{cf.bold('Timestamp')} {format_datetime(dt=change.timestamp)} "
                    f"| {format_datetime(dt=change.timestamp, style=TimestampStyle.RELATIVE)}",
                ]
                copy = change_str.copy()
                for string in change_str:
                    if not string:
                        copy.remove(string)

                embed.add_field(
                    name=change.type.title(),
                    value="\n".join(copy),
                    inline=False,
                )
            pages.append(embed)

        return SimpleMenu(pages)

    async def history(
        self,
        ctx: commands.Context,
        *,
        targets: list[abc.User | PartialUser | abc.GuildChannel | Thread | PartialChannel] | None = None,
        moderators: list[abc.User | PartialUser] | None = None,
        on: date | None = None,
        before: datetime | None = None,
        after: datetime | None = None,
        expired: bool = MISSING,
        resolved: bool = MISSING,
        types: list[ModerationType] | None = None,
        pagesize: int = 6,
        inline: bool = True,
    ) -> SimpleMenu:
        """_summary_.

        Args:
            ctx: _description_
            targets: _description_.
            moderators: _description_.
            on: _description_.
            before: _description_.
            after: _description_.
            expired: _description_.
            resolved: _description_.
            types: _description_.
            pagesize: _description_.
            inline: _description_.

        Raises:
            ValueError: If `pagesize` is lower than 1 or higher than 18, or if the context passed through `ctx` does not have an attached guild.

        Returns:
            The created SimpleMenu, which you can then start with [`await SimpleMenu.start(ctx)`][redbot.core.utils.views.SimpleMenu.start].
        """
        if not ctx.guild:
            msg = "Cannot be used outside of a guild!"
            raise ValueError(msg)

        max_pagesize = 18
        min_pagesize = 1

        if pagesize > max_pagesize:
            msg = f"'pagesize`' cannot be higher than {max_pagesize}!"
            raise ValueError(msg)

        if pagesize < min_pagesize:
            msg = f"'pagesize' cannot be lower than {min_pagesize}!"
            raise ValueError(msg)

        query_construction_before = utcnow()

        guild = await PartialGuild.upsert(ctx.guild)
        where: list[Where | Or] = [Moderation.guild_id == guild.id]

        user_targets: list[PartialUser] = []
        channel_targets: list[PartialChannel] = []
        for t in targets or []:
            if isinstance(t, abc.User):
                user_targets.append(await PartialUser.upsert(user=t))
            elif isinstance(t, (abc.GuildChannel, Thread)):
                channel_targets.append(await PartialChannel.upsert(channel=t))

        if user_targets and channel_targets:
            where.append(
                Moderation.target_user_id.id.is_in([user.id for user in user_targets])
                | Moderation.target_channel_id.id.is_in([channel.id for channel in channel_targets])
            )
        elif user_targets:
            where.append(Moderation.target_user_id.id.is_in([user.id for user in user_targets]))
        elif channel_targets:
            where.append(Moderation.target_channel_id.id.is_in([channel.id for channel in channel_targets]))

        partial_moderators: list[PartialUser] = []
        for m in moderators or []:
            if isinstance(m, abc.User):
                partial_moderators.append(await PartialUser.upsert(user=m))
            else:
                partial_moderators.append(m)

        if partial_moderators:
            where.append(Moderation.moderator_id.is_in([moderator.id for moderator in partial_moderators]))

        if types:
            raw_types = [moderation_type.key for moderation_type in types]
            where.append(Moderation.type_key.is_in(raw_types))

        if on:
            where.append(Moderation.timestamp == on)
        elif before or after:
            if before:
                where.append(Moderation.timestamp < before)
            if after:
                where.append(Moderation.timestamp > after)

        if expired is True:
            where.append(Moderation.expired.eq(True))
        elif expired is False:
            where.append(Moderation.expired.eq(False))

        if resolved is True:
            where.append(Moderation.resolved.eq(True))
        elif resolved is False:
            where.append(Moderation.resolved.eq(True))

        query_construction_after = utcnow()
        query_construction_delta = query_construction_after - query_construction_before
        query_construction_milliseconds = round(number=query_construction_delta.total_seconds() * 1_000, ndigits=3)

        query_before = utcnow()
        query = Moderation.objects(Moderation.all_related()).where(*where).order_by(Moderation.id, ascending=False)
        if not (moderations := await query):
            return SimpleMenu(pages=[cf.error(text="No infractions found matching the given query!")], delete_after_timeout=True)

        query_after = utcnow()
        query_delta = query_after - query_before
        query_milliseconds = round(number=query_delta.total_seconds() * 1_000, ndigits=3)

        count = len(moderations)
        pages: list[_ACCEPTABLE_PAGE_TYPES] = []

        total_pages = (count + pagesize - 1) // pagesize
        embed_color = await ctx.embed_color()
        timestamp = utcnow()
        icon_url = None
        if ctx.guild.icon:
            icon_url = ctx.guild.icon.url
        elif self.me.avatar:
            icon_url = self.me.avatar.url

        moderation_deltas: list[timedelta] = []

        for i in range(0, count, pagesize):
            moderation_before = utcnow()
            embed = Embed(color=embed_color)
            embed.set_author(name="Infraction History", icon_url=icon_url)
            embed.set_footer(text=f"Page {i // pagesize + 1:,}/{total_pages:,} | {count:,} Results")
            embed.timestamp = timestamp

            for moderation in moderations[i : i + pagesize]:
                target: PartialUser | PartialChannel | None = None

                if moderation.target_user_id.user_id:
                    target = moderation.target_user_id
                elif moderation.target_channel_id.channel_id:
                    target = moderation.target_channel_id

                if not target:
                    self._internal_logger.error("Moderation %i does not have a target!", moderation.id)
                    continue

                moderator: PartialUser = moderation.moderator_id

                target_in_guild = self.is_in_guild(partial_object=target, guild=ctx.guild)
                moderator_in_guild = self.is_in_guild(partial_object=moderator, guild=ctx.guild)

                value = (
                    f"{cf.bold(text='Target:')} {target.mention if target_in_guild else cf.inline(text=target.name)} "
                    f"({cf.inline(text=str(target.discord_id))})\n"
                    f"{cf.bold(text='Moderator:')} {moderator.mention if moderator_in_guild else cf.inline(text=moderator.name)} "
                    f"({cf.inline(text=str(moderator.discord_id))})\n"
                    f"{cf.bold(text='Reason:')} {cf.inline(text=moderation.reason or 'No reason provided.')}\n"
                    f"{cf.bold(text='Timestamp:')} {format_datetime(dt=moderation.timestamp, style=TimestampStyle.LONG_DATE_AND_TIME)}"
                    f" | {format_datetime(dt=moderation.timestamp, style=TimestampStyle.RELATIVE)}\n"
                )

                if moderation.duration:
                    value += f"{cf.bold(text='Duration:')} {cf.humanize_timedelta(timedelta=moderation.duration)}"
                    if moderation.expired:
                        value += " | Expired\n"
                    elif moderation.end_timestamp:
                        value += f" | {format_datetime(dt=moderation.end_timestamp, style=TimestampStyle.RELATIVE)}\n"

                if moderation.resolved:
                    value += f"{cf.bold(text='Resolved:')} {moderation.resolved}\n"

                    if moderation.resolve_reason:
                        value += f"{cf.bold(text='Resolve Reason:')} {cf.inline(text=moderation.resolve_reason or 'No reason provided.')}\n"

                try:
                    moderation_type = moderation.type
                except RegistryKeyError:
                    moderation_type = None

                if moderation_type:
                    for key, content in moderation.meta.items():
                        if key in moderation.type.history_metadata:
                            value += f"{cf.bold(title(key) + ':')} {content}\n"

                embed.add_field(name=f"Case {moderation.id:,} ({title(moderation.type_key)})", value=value, inline=inline)
            pages.append(embed)
            moderation_after = utcnow()
            moderation_deltas.append(moderation_after - moderation_before)

        total_moderation_time = sum(moderation_deltas, timedelta(0))
        moderation_milliseconds = total_moderation_time.total_seconds() * 1_000
        total_ms = query_construction_milliseconds + query_milliseconds + moderation_milliseconds
        moderation_average = (total_moderation_time / len(moderation_deltas)).total_seconds() * 1_000
        moderation_highest = max(moderation_deltas, default=timedelta(0)).total_seconds() * 1_000

        self._internal_logger.trace(
            f"History query completed in {total_ms:,.3f} ms! "
            f"Query construction time: '{query_construction_milliseconds:,.3f} ms' "
            f"Query time: '{query_milliseconds:,.3f} ms' "
            f"Moderation iteration time: '{moderation_milliseconds:,.3f} ms' "
            f"Longest moderation iteration: '{moderation_highest:,.3f} ms' "
            f"Avg. time per moderation: '{moderation_average:,.3f} ms'"
        )

        return SimpleMenu(pages=pages, timeout=240, use_select_menu=True)

    @tasks.loop(minutes=1)
    async def _sentinel_monitor_expiry_loop(self) -> None:
        await self.bot.wait_until_red_ready()
        loop = SentinelCog._sentinel_expiry_loop
        if loop is None or not loop.is_running():
            SentinelCog._sentinel_expiry_loop = self._sentinel_expiry_handler
            try:
                SentinelCog._sentinel_expiry_loop.start()
                self._sentinel_logger.debug("Took over expiry loop!")
            except RuntimeError:  # Race condition?
                pass

    @tasks.loop(minutes=1)
    async def _sentinel_expiry_handler(self) -> None:
        await self.bot.wait_until_red_ready()
        current_time = utcnow()
        global_num = 0
        global_err_num = 0

        guilds = [await PartialGuild.upsert(guild) for guild in self.bot.guilds if not await self.bot.cog_disabled_in_guild(self, guild)]
        moderations = (
            await Moderation.objects()
            .where(
                Moderation.duration.is_not_null(),
                Moderation.expired.eq(False),
                Moderation.guild_id.is_in([guild.id for guild in guilds]),
            )
            .order_by(Moderation.guild_id)
        )
        expirable_moderations: dict[int, list[Moderation]] = defaultdict(list)
        for moderation in moderations:
            try:
                if moderation.type.can_expire:
                    expirable_moderations[moderation.guild_id].append(moderation)
            except ValueError:  # noqa: PERF203
                pass
            except RegistryKeyError:
                self._sentinel_logger.warning("Attempted to expire a moderation with an invalid moderation type: %s", moderation.type_key)
                global_err_num += 1

        for guild in guilds:
            time_per_guild = utcnow()
            num = 0
            err_num = 0

            for moderation in expirable_moderations[guild.id]:
                try:
                    await moderation.expire()
                    num += 1
                except ValueError as err:  # noqa: PERF203
                    self._sentinel_logger.exception(err)
                    err_num += 1
                except NotImplementedError as err:
                    self._sentinel_logger.trace("Attempted to expire a moderation with a non-expirable moderation type!", exc_info=err)
                    err_num += 1

            per_guild_completion_time = utcnow() - time_per_guild
            self._sentinel_logger.verbose(
                "Completed expiry loop for guild '%s' (%s) in %sms with %s successful cases and %s errors.",
                guild.name,
                guild.guild_id,
                round(number=per_guild_completion_time.total_seconds() * 1000, ndigits=3),
                num,
                err_num,
            )
            global_num += num
            global_err_num += err_num

        completion_time = utcnow() - current_time
        self._sentinel_logger.debug(
            "Completed expiry loop for %s guilds in %sms with %s successful cases and %s errors.",
            len(guilds),
            round(number=completion_time.total_seconds() * 1000, ndigits=3),
            global_num,
            global_err_num,
        )
