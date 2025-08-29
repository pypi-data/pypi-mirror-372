# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
# © 2025 cswimr

"""Defines the base class for Sentinel moderation types."""

from types import CoroutineType
from typing import TYPE_CHECKING, Any, Callable

from class_registry.registry import ClassRegistry
from discord import Interaction, Member, Permissions, Thread, User, abc
from redbot.core import commands
from typing_extensions import override

from tidegear.utils import class_overrides_method

if TYPE_CHECKING:
    from tidegear.sentinel.db.tables import Moderation


class ModerationType:
    r"""This is a base class for Sentinel moderation types.

    Example:
        ```python
        from discord import Member, Permissions, User
        from redbot.core import commands
        from redbot.core.utils import chat_formatting as cf
        from typing_extensions import override

        from tidegear.sentinel.db import Moderation, PartialGuild, PartialUser
        from tidegear.sentinel.type import ModerationType


        class Warn(ModerationType):
            key = "warn"
            string = "warn"
            verb = "warned"
            permissions = Permissions(moderate_members=True)

            @override
            @classmethod
            async def user_target_handler(cls, ctx: commands.Context, target: User | Member, reason: str) -> Moderation:
                assert ctx.guild
                response = await ctx.send(
                    content=f"{target.mention} has {cls.embed_desc}{cls.verb}!\n{cf.bold(text='Reason')} - {cf.inline(text=reason)}"
                )

                partial_target = await PartialUser.upsert(user=target)
                partial_moderator = await PartialUser.upsert(user=ctx.author)
                partial_guild = await PartialGuild.upsert(guild=ctx.guild)
                moderation = Moderation(
                    _data={
                        Moderation.guild_id: partial_guild.id,
                        Moderation.type_key: cls.key,
                        Moderation.target_user_id: partial_target.id,
                        Moderation.moderator_id: partial_moderator.id,
                        Moderation.reason: reason,
                    }
                )
                await moderation.save()
                await response.edit(
                    content=(
                        f"{target.mention} has {cls.embed_desc}{cls.verb}! (Case: {cf.inline(f'#{moderation.id:,}')})"
                        f"\n{cf.bold(text='Reason:')} {cf.inline(text=reason)}"
                    )
                )
                return moderation

            @override
            @classmethod
            async def resolve_handler(cls, moderation: Moderation, reason: str) -> None:
                return
        ```

    Attributes:
        key: The key to use for this type. This should be unique, as this is how the type is registered internally.
            Changing this key will break existing cases with this type.
            Defaults to `type`.
        string: The string to display for this type. Defaults to `type`.
        verb: The verb to use for this type. Defaults to `typed`.
        embed_desc: The string to use for embed descriptions. Defaults to `been `.
        removes_from_guild: Whether this type's handler removes the target from the guild,
            or if the moderation is expected to occur whenever the user is not in the guild.
            This does not actually remove the target from the guild; the handler method is responsible for that.
            Defaults to `False`.
        permissions: The Discord permissions required for this type's moderation handler to function.
            Defaults to [`Permissions.none`][discord.Permissions.none].
        history_metadata: A set of metadata keys to make visible in the output of [`SentinelCog.history`][tidegear.sentinel.SentinelCog.history].
            Defaults to [`set`][].
    """

    key: str = "type"
    string: str = "type"
    verb: str = "typed"
    embed_desc: str = "been "
    removes_from_guild: bool = False
    permissions: Permissions = Permissions.none()
    history_metadata: set[str] = set()

    @property
    def can_edit_duration(self) -> bool:
        """Check whether or not this type overrides the `edit_duration_handler` method.

        Returns:
            If this type supports editing the duration of moderations.
        """
        return class_overrides_method(child=type(self), parent=ModerationType, method_name="edit_duration_handler")

    @property
    def can_expire(self) -> bool:
        """Check whether or not this type overrides the `expiry_handler` method.

        Returns:
            If this type supports moderation expiry.
        """
        return class_overrides_method(child=type(self), parent=ModerationType, method_name="expiry_handler")

    @property
    def can_target_channels(self) -> bool:
        """Check whether or not this type overrides the `channel_target_handler` method.
        Consider using [`.handler`][tidegear.sentinel.ModerationType.handler] instead
        if you just want to retrieve the correct handler for a [`User`][discord.User] or [`GuildChannel`][discord.abc.GuildChannel] object.

        Returns:
            If this type supports targeting channels.
        """
        return class_overrides_method(child=type(self), parent=ModerationType, method_name="channel_target_handler")

    @property
    def can_target_users(self) -> bool:
        """Check whether or not this type overrides the `user_target_handler` method.
        Consider using [`.handler`][tidegear.sentinel.ModerationType.handler] instead
        if you just want to retrieve the correct handler for a [`User`][discord.User] or [`GuildChannel`][discord.abc.GuildChannel] object.

        Returns:
            If this type supports targeting users.
        """
        return class_overrides_method(child=type(self), parent=ModerationType, method_name="user_target_handler")

    @property
    def is_resolvable(self) -> bool:
        """Check whether or not this type overrides the `resolve_handler` method.

        Returns:
            If this type supports being resolved.
        """
        return class_overrides_method(child=type(self), parent=ModerationType, method_name="resolve_handler")

    @property
    def name(self) -> str:
        """Returns the string to display for this type. This is an alias for the `string` attribute."""
        return self.string

    @override
    def __str__(self) -> str:
        """Return the value of `self.string`."""
        return self.string

    @override
    def __repr__(self) -> str:
        attrs = [
            ("key", self.key),
            ("removes_from_guild", self.removes_from_guild),
        ]
        joined = " ".join(f"{key}={value!r}" for key, value in attrs)
        return f"<{self.__class__.__name__} {joined}>"

    def handler(self, target: Member | User | abc.GuildChannel | Thread) -> "Callable[..., CoroutineType[Any, Any, Moderation]]":
        """Returns the proper handler method for the given target type.

        Example:
            ```python
            # assuming `ctx` is a `commands.Context` object,
            # this runs the `user_target_handler` for the `Warn` type if it is defined.
            await Warn().handler(target=ctx.author)(ctx=ctx, target=target)
            ```

        Args:
            target: The target you'd like to retrieve the handler for.

        Raises:
            TypeError: Raised if the type does not support targeting the target type given,
                or if the target type given does not match this method's typehints.

        Returns:
            The resulting handler method.
        """
        if isinstance(target, (Member, User)):
            if not self.can_target_users:
                msg = f"Moderation type {type(self)} does not support targeting users!"
                raise TypeError(msg)
            return self.user_target_handler

        if isinstance(target, (abc.GuildChannel, Thread)):
            if not self.can_target_channels:
                msg = f"Moderation type {type(self)} does not support targeting channels!"
                raise TypeError(msg)
            return self.channel_target_handler

        msg = f"Type {type(target).__name__} is an invalid target type!"
        raise TypeError(msg)

    @classmethod
    async def user_target_handler(cls, ctx: commands.Context, target: Member | User, **kwargs: Any) -> "Moderation":
        """This method should be overridden by any child classes that can target users, but should retain the same starting keyword arguments.

        Args:
            ctx: The context of the command.
            target: The target of the moderation.
            **kwargs (dict[str, Any]): Any additional keyword arguments;
                will be passed in by the [`SentinelCog.moderate`][tidegear.sentinel.SentinelCog.moderate] function.

        Returns:
            The resulting moderation.
        """
        raise NotImplementedError

    @classmethod
    async def channel_target_handler(cls, ctx: commands.Context, target: abc.GuildChannel | Thread, **kwargs: Any) -> "Moderation":
        """This method should be overridden by any child classes that can target channels or threads,
            but should retain the same starting keyword arguments.

        Args:
            ctx: The context of the command.
            target: The target of the moderation.
            **kwargs (dict[str, Any]): Any additional keyword arguments;
                will be passed in by the [`SentinelCog.moderate`][tidegear.sentinel.SentinelCog.moderate] function.

        Returns:
            The resulting moderation.
        """
        raise NotImplementedError

    @classmethod
    async def resolve_handler(cls, moderation: "Moderation", reason: str) -> None:
        """This method should be overridden by any resolvable child classes, but should retain the same keyword arguments.
            If your moderation type should not be resolvable, do not override this.

        Args:
            moderation: The moderation to resolve.
            reason: The reason for resolving the moderation.
        """
        raise NotImplementedError

    @classmethod
    async def expiry_handler(cls, moderation: "Moderation") -> None:
        """This method should be overridden by any expirable child classes, but should retain the same keyword arguments.
            If your moderation type should not expire, do not override this.

        Args:
            moderation: The moderation that is expiring.
        """
        raise NotImplementedError

    @classmethod
    async def duration_edit_handler(cls, interaction: Interaction, old_moderation: "Moderation", new_moderation: "Moderation") -> None:
        """This method should be overridden by any child classes with editable durations, but should retain the same keyword arguments.
            If your moderation type's duration should not be editable, do not override this.

        Args:
            interaction: The interaction that triggered the duration edit.
            old_moderation: The old moderation, from before the `/edit` command was invoked.
            new_moderation: The current state of the moderation.
        """
        raise NotImplementedError


moderation_type_registry: ClassRegistry[ModerationType] = ClassRegistry(attr_name="key", unique=True)
""""""
