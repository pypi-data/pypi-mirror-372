#
# Copyright (C) 2025 Masaryk University
#
# MU-INVENIO-CLI is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Base abstract state class for the MU Invenio CLI application."""

import json
from abc import ABC, abstractmethod


class BaseState(ABC):
    def __init__(self, context):
        self.context = context

    @abstractmethod
    def handle(self):
        pass

    def print_create_json_body(self):
        print("\n" + json.dumps(self.context.create_json_body, indent=4, ensure_ascii=False))

    def print_selected_data(self):
        print("\n" + json.dumps(self.context.selected_data, indent=4, ensure_ascii=False))
