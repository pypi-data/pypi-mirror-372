# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
# © 2025 cswimr

"""Piccolo app configuration."""

import os

from piccolo.conf.apps import AppConfig, table_finder

CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

APP_CONFIG = AppConfig(
    app_name="TidegearSentinel",
    table_classes=table_finder(["tidegear.sentinel.db.tables"]),
    migrations_folder_path=os.path.join(CURRENT_DIRECTORY, "migrations"),
)
