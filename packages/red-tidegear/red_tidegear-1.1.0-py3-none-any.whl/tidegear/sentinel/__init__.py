# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
# © 2025 cswimr

from importlib.util import find_spec
from warnings import warn

warn("Tidegear Sentinel is still a heavy work-in-progress, and it has been imported!")

if not find_spec("redbot_orm"):
    msg = "redbot-orm is not installed, but the `tidegear.sentinel` module was imported! Did you install tidegear with the `sentinel` extra?"
    raise ImportError(msg)

if not find_spec("class_registry"):
    msg = "phx-class-registry is not installed, but the `tidegear.sentinel` module was imported! Did you install tidegear with the `sentinel` extra?"
    raise ImportError(msg)

from .cog import SentinelCog
from .db import Change, Moderation, PartialChannel, PartialGuild, PartialUser
from .type import ModerationType, moderation_type_registry

__all__ = ["Change", "SentinelCog", "Moderation", "PartialChannel", "PartialGuild", "PartialUser", "ModerationType", "moderation_type_registry"]
