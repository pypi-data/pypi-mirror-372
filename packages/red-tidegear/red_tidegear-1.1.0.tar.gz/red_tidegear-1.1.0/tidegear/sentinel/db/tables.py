# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
# © 2025 cswimr

"""Sentinel database table models."""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Literal, Self, overload

import orjson
import rich.repr
from class_registry.base import RegistryKeyError
from discord import Guild, Member, Object, Thread, User, abc
from piccolo.columns.column_types import JSON, Boolean, ForeignKey, Integer, Interval, Serial, Text, Timestamptz, Varchar
from piccolo.columns.defaults.timestamptz import TimestamptzNow
from piccolo.table import Table as BaseTable
from redbot.core.bot import Red
from typing_extensions import override

from tidegear.sentinel.type import ModerationType, moderation_type_registry


class Table(BaseTable):
    """Subclass of Piccolo's Table class that allows for easier pretty printing of table rows."""

    @override
    def __str__(self) -> str:
        return self.__repr__()

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.to_dict()})"

    def __rich_repr__(self) -> rich.repr.Result:  # noqa: D105, PLW3201
        for column, value in self.to_dict().items():
            yield column, value

    __rich_repr__.angular = True  # pyright: ignore[reportFunctionMemberAccess]


class PartialGuild(Table):
    id = Serial(index=True, primary_key=True)
    guild_id = Integer(unique=True, index=True)
    last_known_name = Varchar(default="Unknown Guild", length=100)
    last_updated = Timestamptz(default=datetime.now, null=False)

    @property
    def name(self) -> str:
        return self.last_known_name

    @property
    def discord_object(self) -> Object:
        return Object(id=self.guild_id, type=Guild)

    @property
    def discord_id(self) -> int:
        return self.discord_object.id

    @overload
    async def fetch(self, bot: Red, *, fetch: Literal[True] = ..., upsert: bool = ...) -> Guild: ...

    @overload
    async def fetch(self, bot: Red, *, fetch: Literal[False] = False, upsert: bool = ...) -> Guild | None: ...

    async def fetch(self, bot: Red, *, fetch: bool = False, upsert: bool = True) -> Guild | None:
        """Retrieve a Guild object for this PartialGuild. Only use this if you need more information than is stored within the database.

        Args:
            bot: The bot object to use to retrieve the guild.
            fetch: Whether or not to attempt to fetch the guild from Discord's API if the guild is not in the internal cache.
                Avoid using this unless absolutely necessary, as this endpoint is ratelimited and introduces additional runtime cost.
            upsert: Whether or not to automatically upsert the retrieved Guild object into the database.
                This introduces a minimal runtime cost if you're already fetching from the Discord API, and should usually be done.

        Returns:
            The retrieved guild object, or None if `fetch` is `False` and the guild is not in the bot's internal cache.
        """
        guild = bot.get_guild(self.guild_id)
        if fetch and not guild:
            guild = await bot.fetch_guild(self.guild_id)
        if upsert and guild:
            await self.upsert(guild)
        return guild

    @classmethod
    async def upsert(cls, guild: Guild) -> Self:
        """Insert or update a row in the database based on metadata from a Guild object.

        Args:
            guild: The guild object to upsert.

        Raises:
            ValueError: If upserting fails for some reason.

        Returns:
            (PartialGuild): The resulting PartialGuild object.
        """
        query = cls.objects().where(cls.guild_id == guild.id).first()
        if fetched_guild := await query:
            await fetched_guild.update_self(values={cls.last_known_name: guild.name, cls.last_updated: TimestamptzNow().python()})
            return fetched_guild

        await cls.insert(cls(_data={cls.guild_id: guild.id, cls.last_known_name: guild.name}))
        if result := await query:
            return result
        msg = "Upsert operation failed!"
        raise ValueError(msg)


class PartialUser(Table):
    id = Serial(index=True, primary_key=True)
    user_id = Integer(unique=True, index=True)
    last_known_name = Varchar(default="Unknown User", length=32)
    discriminator = Integer(null=True)
    last_updated = Timestamptz(default=datetime.now, null=False)

    @property
    def name(self) -> str:
        if self.discriminator and self.discriminator != 0:
            return f"{self.last_known_name}#{self.discriminator}"
        return self.last_known_name

    @property
    def mention(self) -> str:
        return f"<@{self.user_id}>"

    @property
    def discord_object(self) -> Object:
        return Object(id=self.user_id, type=User)

    @property
    def discord_id(self) -> int:
        return self.discord_object.id

    @overload
    async def fetch(self, fetcher: Red, *, fetch: Literal[True] = ..., upsert: bool = ...) -> User: ...
    @overload
    async def fetch(self, fetcher: Red, *, fetch: Literal[False] = False, upsert: bool = ...) -> User | None: ...
    @overload
    async def fetch(self, fetcher: Guild, *, fetch: Literal[True] = ..., upsert: bool = ...) -> Member: ...
    @overload
    async def fetch(self, fetcher: Guild, *, fetch: Literal[False] = False, upsert: bool = ...) -> Member | None: ...

    async def fetch(self, fetcher: Red | Guild, *, fetch: bool = False, upsert: bool = True) -> User | Member | None:
        """Retrieve a User or Member object for this PartialUser. Only use this if you need more information than is stored within the database.

        Args:
            fetcher: The object to use to retrieve the User or Member.
            fetch: Whether or not to attempt to fetch the user from Discord's API if the user is not in the internal cache.
                Avoid using this unless absolutely necessary, as this endpoint is ratelimited and introduces additional runtime cost.
            upsert: Whether or not to automatically upsert the retrieved User / Member object into the database.
                This introduces a minimal runtime cost if you're already fetching from the Discord API, and should usually be done.

        Raises:
            TypeError: Raised if `fetcher` is not a supported type.

        Returns:
            The retrieved User / Member object, or None if `fetch` is `False` and the user is not in the bot's internal cache.
        """
        if isinstance(fetcher, Red):
            user = fetcher.get_user(self.user_id)
            if fetch and not user:
                user = await fetcher.fetch_user(self.user_id)
        elif isinstance(fetcher, Guild):
            user = fetcher.get_member(self.user_id)
            if fetch and not user:
                user = await fetcher.fetch_member(self.user_id)
        else:
            msg = f"Unsupported fetcher type: {type(fetcher).__name__}"
            raise TypeError(msg)

        if upsert and user:
            await self.upsert(user)
        return user

    @classmethod
    async def upsert(cls, user: abc.User) -> Self:
        """Insert or update a row in the database based on metadata from a User object.

        Args:
            user: The User object to upsert.

        Raises:
            ValueError: If upserting fails for some reason.

        Returns:
            (PartialUser): The resulting PartialUser object.
        """
        query = cls.objects().where(cls.user_id == user.id).first()
        if fetched_user := await query:
            await fetched_user.update_self(
                values={cls.last_known_name: user.name, cls.discriminator: int(user.discriminator), cls.last_updated: TimestamptzNow().python()}
            )
            return fetched_user

        await cls.insert(cls(_data={cls.user_id: user.id, cls.last_known_name: user.name, cls.discriminator: int(user.discriminator)}))
        if result := await query:
            return result
        msg = "Upsert operation failed!"
        raise ValueError(msg)


class PartialChannel(Table):
    id = Serial(index=True, primary_key=True)
    guild_id = ForeignKey(references=PartialGuild, null=False)
    channel_id = Integer(index=True)
    last_known_name = Varchar(default="Unknown Channel", length=100)
    last_updated = Timestamptz(default=datetime.now, null=False)

    @property
    def name(self) -> str:
        return f"#{self.last_known_name}"

    @property
    def mention(self) -> str:
        return f"<#{self.channel_id}>"

    @property
    def discord_object(self) -> Object:
        return Object(id=self.channel_id, type=abc.GuildChannel)

    @property
    def discord_id(self) -> int:
        return self.discord_object.id

    @overload
    async def fetch(self, bot: Red, *, fetch: Literal[True] = ..., upsert: bool = ...) -> abc.GuildChannel | Thread: ...

    @overload
    async def fetch(self, bot: Red, *, fetch: Literal[False] = False, upsert: bool = ...) -> abc.GuildChannel | Thread | None: ...

    async def fetch(self, bot: Red, *, fetch: bool = False, upsert: bool = True) -> abc.GuildChannel | Thread | None:
        """Retrieve a GuildChannel or Thread object for this PartialChannel.

        Only use this if you need more information than is stored within the database.

        Args:
            bot: The bot object to use to retrieve the channel.
            fetch: Whether or not to attempt to fetch the channel from Discord's API if the channel is not in the internal cache.
                Avoid using this unless absolutely necessary, as this endpoint is ratelimited and introduces additional runtime cost.
            upsert: Whether or not to automatically upsert the retrieved GuildChannel / Thread object into the database.
                This introduces a minimal runtime cost if you're already fetching from the Discord API, and should usually be done.

        Returns:
            The retrieved channel object, or None if `fetch` is `False` and the guild or channel is not in the bot's internal cache.
        """
        partial_guild = await self.guild()
        if not (guild := await partial_guild.fetch(bot, fetch=fetch)):
            return None

        channel = guild.get_channel_or_thread(self.channel_id)
        if fetch and not channel:
            channel = await guild.fetch_channel(self.channel_id)

        if upsert and channel:
            await self.upsert(channel)
        return channel

    async def guild(self, /, *, cache: bool = True) -> PartialGuild:
        """Retrieve the [`PartialGuild`][tidegear.sentinel.PartialGuild] that this channel belongs to.

        Args:
            cache: Whether or not to try an internal cache before querying the database.
                This will have no effect if you haven't ran this method yet on this PartialChannel instance.

        Raises:
            ValueError: If the guild tied to this channel no longer exists in the database.
                This should be reported as a bug if it occurs, as there's a foreign key constraint that should prevent this on the table itself.

        Returns:
            The guild object tied to this channel.
        """
        if cache and "_guild_obj" in self.__dict__:
            return self._guild_obj

        if not (guild := await PartialGuild.objects().where(PartialGuild.id == self.guild_id).first()):
            msg = f"No guild exists in the database with id {self.guild_id}!"
            raise ValueError(msg)

        self._guild_obj = guild
        return self._guild_obj

    @classmethod
    async def upsert(cls, channel: abc.GuildChannel | Thread) -> Self:
        """Insert or update a row in the database based on metadata from a GuildChannel or Thread object.

        Args:
            channel: The channel object to upsert.

        Raises:
            ValueError: If upserting fails for some reason.

        Returns:
            (PartialChannel): The resulting PartialChannel object.
        """
        query = cls.objects(cls.guild_id).where(cls.channel_id == channel.id, cls.guild_id.guild_id == channel.guild.id).first()
        if fetched_channel := await query:
            await fetched_channel.update_self(values={cls.last_known_name: channel.name, cls.last_updated: TimestamptzNow().python()})
            return fetched_channel

        guild = await PartialGuild.upsert(guild=channel.guild)
        await cls.insert(cls(_data={cls.guild_id: guild.id, cls.channel_id: channel.id, cls.last_known_name: channel.name}))

        if result := await query:
            return result
        msg = "Upsert operation failed!"
        raise ValueError(msg)


class Change(Table):
    class Type(StrEnum):
        ORIGINAL = "original"
        RESOLVE = "resolve"
        EDIT = "edit"

    id = Serial(index=True, primary_key=True)
    moderation_id = ForeignKey(references="Moderation", null=False)
    type = Varchar(choices=Type, null=False)
    timestamp = Timestamptz(default=datetime.now, null=False)
    moderator_id = ForeignKey(references=PartialUser, null=False)
    reason = Text(default=None, null=True)
    duration = Interval(default=None, null=True)

    @property
    def end_timestamp(self) -> datetime | None:
        if self.timestamp and self.duration:
            return self.timestamp + self.duration
        return None

    async def moderation(self, /, *, cache: bool = True) -> "Moderation":
        if cache and "_moderation_obj" in self.__dict__:
            return self._moderation_obj

        if not (mod := await Moderation.objects().where(Moderation.id == self.moderation_id).first()):
            msg = f"Moderation with id {self.moderation_id} does not exist in the database!"
            raise ValueError(msg)

        self._moderation_obj = mod
        return mod

    async def moderator(self, /, *, cache: bool = True) -> PartialUser:
        if cache and "_moderator_obj" in self.__dict__:
            return self._moderator_obj

        if not (user := await PartialUser.objects().where(PartialUser.id == self.moderator_id).first()):
            msg = f"PartialUser with id {self.moderator_id} does not exist in the database!"
            raise ValueError(msg)

        self._moderator_obj = user
        return user


class Moderation(Table):
    id = Serial(index=True, primary_key=True)
    guild_id = ForeignKey(references=PartialGuild, null=False, index=True)
    timestamp = Timestamptz(default=datetime.now, null=False, index=True)
    type_key = Varchar(default=None, null=False, db_column_name="type")
    target_user_id = ForeignKey(references=PartialUser, null=True, index=True)
    target_channel_id = ForeignKey(references=PartialChannel, null=True, index=True)
    moderator_id = ForeignKey(references=PartialUser, null=False, index=True)
    duration = Interval(default=None, null=True)
    expired = Boolean(default=False, null=False)
    reason = Text(default=None, null=True)
    resolved = Boolean(default=False, null=False)
    resolver_id = ForeignKey(references=PartialUser, null=True, index=True)
    resolve_reason = Text(default=None, null=True)
    metadata = JSON(default="{}", null=False)

    @property
    def end_timestamp(self) -> datetime | None:
        """Retrieve the datetime at which the moderation should expire, if it has a duration.

        Warning:
            This property does not check if the moderation's type supports expiry.
            Instead, use [`.type.can_expire`][tidegear.sentinel.ModerationType.can_expire] for that.

        Returns:
            The datetime at which the moderation should expire, or `None` if the moderation does not have a duration set.
        """
        if self.duration:
            return self.timestamp + self.duration
        return None

    @property
    def type(self) -> ModerationType:
        """Retrieve the moderation's case type. This gives you access to all of the type's handler methods.

        Raises:
            RegistryKeyError: If the case type does not exist in the [type registry][tidegear.sentinel.moderation_type_registry].

        Returns:
            The moderation's case type.
        """
        try:
            return moderation_type_registry.get(key=self.type_key)
        except RegistryKeyError as err:
            msg = f"Moderation type with key '{self.type_key}' does not exist in the moderation type registry!"
            raise RegistryKeyError(msg) from err

    @property
    def meta(self) -> dict[str, Any]:
        data: dict[str, Any] = orjson.loads(self.metadata)
        return data

    async def changes(self, /, *, cache: bool = True) -> list[Change]:
        if cache and "_changes" in self.__dict__:
            return self._changes

        changes = await Change.objects().where(Change.moderation_id == self.id)

        self._changes = changes
        return changes

    async def guild(self, /, *, cache: bool = True) -> PartialGuild:
        if cache and "_guild_obj" in self.__dict__:
            return self._guild_obj

        if not (guild := await PartialGuild.objects().where(PartialGuild.id == self.guild_id).first()):
            msg = f"Could not find a PartialGuild in the database with id {self.guild_id}"
            raise ValueError(msg)

        self._guild_obj = guild
        return guild

    async def moderator(self, /, *, cache: bool = True) -> PartialUser:
        if cache and "_moderator_obj" in self.__dict__:
            return self._moderator_obj

        if not (user := await PartialUser.objects().where(PartialUser.id == self.moderator_id).first()):
            msg = f"Could not find a PartialUser in the database with id {self.moderator_id}"
            raise ValueError(msg)

        self._moderator_obj = user
        return user

    async def target(self, /, *, cache: bool = True) -> PartialUser | PartialChannel:
        if cache and "_target_obj" in self.__dict__:
            return self._target_obj

        if self.target_user_id is not None:
            if not (result := await PartialUser.objects().where(PartialUser.id == self.target_user_id).first()):
                msg = f"Could not find a PartialUser in the database with id {self.target_user_id}"
                raise ValueError(msg)

        elif self.target_channel_id is not None:
            if not (result := await PartialChannel.objects().where(PartialChannel.id == self.target_channel_id).first()):
                msg = f"Could not find a PartialChannel in the database with id {self.target_channel_id}"
                raise ValueError(msg)

        else:
            msg = "Neither target_user nor target_channel are set!"
            raise ValueError(msg)

        self._target_obj = result
        return result

    async def resolver(self, /, *, cache: bool = True) -> PartialUser:
        if cache and "_resolver_obj" in self.__dict__:
            return self._resolver_obj

        if not (user := await PartialUser.objects().where(PartialUser.id == self.resolver_id).first()):
            msg = f"Could not find a PartialUser in the database with id {self.resolver_id}"
            raise ValueError(msg)

        self._resolver_obj = user
        return user

    async def expire(self) -> Self:
        if self.expired:
            msg = f"Moderation {self.id:,} is already expired!"
            raise ValueError(msg)

        if self.type.can_expire:
            if self.end_timestamp and datetime.now(tz=UTC) >= self.end_timestamp:
                await self.type.expiry_handler(moderation=self)
                await self.update_self({Moderation.expired: True})
                return self
        msg = f"Moderation of type {self.type.key} is not expirable!"
        raise NotImplementedError(msg)

    @classmethod
    async def delete_for_guild(cls, guild: Guild | PartialGuild) -> list[Self]:
        """Delete all Moderation cases for a specific guild.

        Args:
            guild: The guild to delete cases for.

        Returns:
            (list[Moderation]): The deleted cases.
        """
        if isinstance(guild, Guild):
            guild = await PartialGuild.upsert(guild)
        raw_moderations = await cls.delete().where(cls.guild_id == guild.id).returning(*cls.all_columns())
        return [cls(**moderation) for moderation in raw_moderations]

    @classmethod
    async def next_case_number(cls) -> int:
        """Get the case number of the next moderation to be inserted into the database.

        Returns:
            The case number of the next moderation to be inserted into the database.
        """
        return await cls.count() + 1
