#
# Copyright (C) 2025 Masaryk University
#
# MU-INVENIO-CLI is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Not selected state for the MU Invenio CLI application.
This state handles the actions when no draft is selected.
"""

from mu_invenio_cli.services.record_service import RecordService
from mu_invenio_cli.states.state import State


class NotSelectedState:
    def __init__(self, context):
        self.context = context

    def has_access_to_draft(self, record_id):
        return True

    def handle(self):
        self.clear_state()

        print("\nPlease create a draft or select an existing one.")
        while True:
            print("\nOptions:")
            print("  1. Create a new draft")
            print("  2. Set draft by id")
            print("  8. Back to configuration")
            print("  9. Help")
            print("  0. Exit")

            choice = input("Select option: ").strip()
            if choice == '1':
                self.context.state = State.CREATE
                self.context.last_state = State.NOT_SELECTED
                print("Switching to create state...")
                break
            elif choice == '2':
                record_id = input("Enter record id: ").strip()
                api_client = RecordService(self.context)
                draft = api_client.get_draft(record_id)
                if draft:
                    self.context.selected_data = draft
                    self.context.selected_id = record_id
                    self.context.last_state = State.NOT_SELECTED
                    self.context.state = State.SELECTED
                    break
                else:
                    print(f"Draft with id {record_id} not found or you do not have access to it.")
                    continue
            elif choice == '8':
                self.context.last_state = State.NOT_SELECTED
                self.context.state = State.CONFIGURATION
                print("Returning to configuration state.")
                break
            elif choice == '9':
                self.context.last_state = State.NOT_SELECTED
                self.context.state = State.HELP
                break
            elif choice == '0':
                exit(0)
            else:
                print("Invalid option. Please try again.")

    def clear_state(self):
        self.context.selected_id = None
        self.context.create_json_body = None
        self.context.selected_data = None
