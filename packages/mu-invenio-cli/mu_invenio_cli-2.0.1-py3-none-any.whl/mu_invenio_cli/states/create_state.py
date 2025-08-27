#
# Copyright (C) 2025 Masaryk University
#
# MU-INVENIO-CLI is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#

"""State for creating a new draft in the MU Invenio CLI application."""

import json
import os

from mu_invenio_cli.file_selector import FileSelector
from mu_invenio_cli.services.record_service import RecordService
from mu_invenio_cli.states.base_state import BaseState
from mu_invenio_cli.states.state import State


class CreateState(BaseState):
    def handle(self):
        while True:
            print("\nCreate Draft Options:")
            print("  1. Set file containing draft json data")
            if self.context.create_json_body:
                print("  2. Print draft json data")
            print("  3. Create")
            print("  8. Back")
            print("  9. Help")
            print("  0. Exit")

            choice = input("Select option: ").strip()
            if choice == '1':
                # file_path = input("Enter path to JSON file: ").strip()
                file_path = FileSelector().select_file_path()
                if not os.path.isfile(file_path):
                    print("File does not exist.")
                    continue
                try:
                    with open(file_path, 'r') as f:
                        self.context.create_json_body = json.load(f)
                    print("File loaded successfully.")
                except Exception as e:
                    print(f"Failed to load JSON: \n     {e}")
            elif self.context.create_json_body and choice == '2':
                self.print_create_json_body()
            elif choice == '3':
                api_client = RecordService(self.context)
                created = api_client.create_draft()
                if created:
                    self.context.selected_data = created
                    self.context.selected_id = created["id"]
                    self.context.state = State.SELECTED
                    self.context.last_state = State.CREATE
                    break
                else:
                    print("Failed to create draft. Please check issue and try again.")
            elif choice == '8':
                self.context.state = State.NOT_SELECTED
                self.context.last_state = State.CREATE
                break
            elif choice == '9':
                self.context.last_state = State.CREATE
                self.context.state = State.HELP
                break
            elif choice == '0':
                exit(0)
            else:
                print("Invalid option. Please try again.")


