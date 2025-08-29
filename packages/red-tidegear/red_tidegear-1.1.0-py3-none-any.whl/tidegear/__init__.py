# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
# © 2025 cswimr

from .cog import Cog
from .version import __version__, meta, version

__all__ = [
    "__version__",
    "Cog",
    "meta",
    "version",
]
