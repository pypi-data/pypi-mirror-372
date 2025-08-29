# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
# © 2025 cswimr

"""Piccolo engine and registry configuration."""

import os

from piccolo.conf.apps import AppRegistry
from piccolo.engine.sqlite import SQLiteEngine

if not (path := os.getenv("DB_PATH")):
    msg = "DB_PATH environment variable not set!"
    raise ValueError(msg)

DB = SQLiteEngine(path=path)

APP_REGISTRY = AppRegistry(apps=["tidegear.sentinel.db.piccolo_app"])
