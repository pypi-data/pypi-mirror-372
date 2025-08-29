# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
# © 2025 cswimr

"""A work in progress importer for [Aurora V3](https://c.csw.im/cswimr/SeaCogs/pull/48) moderations."""

from datetime import UTC, datetime, timedelta
from typing import Any, overload

from discord import ButtonStyle, Client, Interaction, Member, Message, NotFound, ui
from piccolo.columns import Column
from redbot.core import commands
from redbot.core.utils import chat_formatting as cf
from typing_extensions import override

from tidegear.sentinel.db import Moderation, PartialChannel, PartialGuild, PartialUser
from tidegear.sentinel.db.tables import Change


def _timedelta_from_string(string: str) -> timedelta:
    """Convert a string to a timedelta object.

    Args:
        string: The string to convert to a timedelta object. Must be in the format `HH:MM:SS`, e.g. `125:47:31`.

    Returns:
        The created timedelta object.
    """
    hours, minutes, seconds = map(int, string.split(":"))
    return timedelta(hours=hours, minutes=minutes, seconds=seconds)


class ImportAuroraV3View(ui.View):  # noqa: D101
    def __init__(self, *, ctx: commands.Context, message: Message, data: list[dict[str, Any]], timeout: float | None = 180) -> None:
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.message = message
        self.data = data

    @override
    async def on_timeout(self) -> None:
        try:
            await self.message.edit(content=self.message.content + "\n" + cf.warning("Timed out!"), view=None)
        except NotFound:
            pass

    @override
    async def interaction_check(self, interaction: Interaction[Client]) -> bool:
        if not interaction.guild or not isinstance(interaction.user, Member):
            return False
        if await self.ctx.bot.is_owner(interaction.user) or interaction.user.guild_permissions.administrator:
            return True
        await interaction.response.send_message("This button is only for bot owners or server administrators.", ephemeral=True)
        return False

    @ui.button(label="Yes", style=ButtonStyle.success)
    async def import_button_y(self, interaction: Interaction, button: ui.Button) -> None:  # noqa: D102
        assert interaction.guild and isinstance(interaction.user, Member)
        await interaction.response.defer()
        guild = await PartialGuild.upsert(guild=interaction.guild)
        users: dict[int, PartialUser] = {}
        channels: dict[int, PartialChannel] = {}

        @overload
        async def get_or_query(object_type: type[PartialUser], object_id: int) -> PartialUser: ...
        @overload
        async def get_or_query(object_type: type[PartialChannel], object_id: int) -> PartialChannel: ...

        async def get_or_query(object_type: type[PartialUser] | type[PartialChannel], object_id: int) -> PartialUser | PartialChannel:
            if object_type is PartialUser:
                if obj := users.get(object_id):
                    return obj

                if user := self.ctx.bot.get_user(object_id):
                    partial = await PartialUser.upsert(user)
                    users[object_id] = partial
                    return partial

                query = PartialUser.objects().where(PartialUser.user_id == object_id).first()
                if not (partial := await query):
                    await PartialUser.insert(PartialUser(_data={PartialUser.user_id: object_id}))
                    if not (partial := await query):
                        msg = "Saving PartialUser to database failed!"
                        raise ValueError(msg)
                users[object_id] = partial
                return partial

            if object_type is PartialChannel:
                if obj := channels.get(object_id):
                    return obj

                if channel := self.ctx.bot.get_channel(object_id):
                    partial = await PartialChannel.upsert(channel)
                    channels[object_id] = partial
                    return partial

                query = PartialChannel.objects().where(PartialChannel.channel_id == object_id, PartialChannel.guild_id == guild.id).first()
                if not (partial := await query):
                    await PartialChannel.insert(PartialChannel(_data={PartialChannel.channel_id: object_id, PartialChannel.guild_id: guild.id}))
                    if not (partial := await query):
                        msg = "Saving PartialChannel to database failed!"
                        raise ValueError(msg)
                channels[object_id] = partial
                return partial

            msg = f"get_or_query only accepts PartialUser or PartialChannel, got {object_type!r}"
            raise TypeError(msg)

        for case in reversed(self.data):
            if case["moderation_id"] == 0:
                continue

            data: dict[Column, Any] = {
                Moderation.guild_id: guild.id,
                Moderation.type_key: case["moderation_type"].lower(),
                Moderation.timestamp: datetime.fromtimestamp(case["timestamp"], tz=UTC),
                Moderation.moderator_id: (await get_or_query(PartialUser, case["moderator_id"])).id,
                Moderation.reason: case.get("reason"),
                Moderation.expired: case.get("expired", False),
                Moderation.resolved: case.get("resolved", False),
                Moderation.resolve_reason: case.get("resolve_reason"),
            }

            target_id = case["target_id"]
            match case["target_type"].lower():
                case "user":
                    target = await get_or_query(PartialUser, target_id)
                    data[Moderation.target_user_id] = target.id
                case "channel":
                    target = await get_or_query(PartialChannel, target_id)
                    data[Moderation.target_channel_id] = target.id
                case _:
                    msg = f"The Aurora importer does not support targets with type {case['target_type']}"
                    raise ValueError(msg)

            if resolver_id := case.get("resolved_by"):
                data[Moderation.resolver_id] = (await get_or_query(PartialUser, resolver_id)).id

            metadata: dict[str, Any] = case.get("metadata", {})
            metadata.update({"imported_from": "Aurora", "imported_timestamp": datetime.now(tz=UTC).isoformat(sep=" ")})

            duration = case.get("duration")
            if duration:
                duration = _timedelta_from_string(duration)

            data.update({Moderation.metadata: metadata, Moderation.duration: duration})

            moderation_id = await Moderation.next_case_number()

            await Moderation.insert(Moderation(_data=data))

            changes: list[dict[str, Any]] = case.get("changes", [])
            for change in changes:
                change_data: dict[Column, Any] = {
                    Change.moderation_id: moderation_id,
                    Change.type: change["type"].lower(),
                    Change.timestamp: datetime.fromtimestamp(change["timestamp"], tz=UTC),
                    Change.moderator_id: (await get_or_query(PartialUser, change["user_id"])).id,
                }

                if reason := change.get("reason"):
                    change_data[Change.reason] = reason
                if duration := change.get("duration"):
                    change_data[Change.duration] = _timedelta_from_string(duration)

                await Change.insert(Change(_data=change_data))

    @ui.button(label="No", style=ButtonStyle.danger)
    async def import_button_n(self, interaction: Interaction, button: ui.Button) -> None:  # noqa: D102
        if interaction.message:
            await interaction.message.edit(content="Import cancelled.", view=None)
            await interaction.message.delete(delay=10)
        await self.ctx.message.delete(delay=10)
