#
# Copyright (C) 2025 Masaryk University
#
# MU-INVENIO-CLI is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""CLI context storage for the MU Invenio CLI application."""

from mu_invenio_cli.states.state import State


class CLIContext:
    def __init__(self):
        self.config = {}
        self.selected_id = None
        self.create_json_body = None
        self.selected_data = None
        self.state = State.CONFIGURATION
        self.last_state = State.CONFIGURATION
