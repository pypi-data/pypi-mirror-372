#
# Copyright (C) 2025 Masaryk University
#
# MU-INVENIO-CLI is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""State for deleting a draft in the MU Invenio CLI application."""

from mu_invenio_cli.services.record_service import RecordService
from mu_invenio_cli.states.base_state import BaseState
from mu_invenio_cli.states.state import State


class DeleteState(BaseState):
    def handle(self):
        while True:
            print(f"\nDo you want to delete draft with id {self.context.selected_id}:")
            print("  1. Confirm")
            print("  2. Cancel")
            print("  9. Help")
            print("  0. Exit")

            choice = input("Select option: ").strip()
            if choice == '1':
                api_client = RecordService(self.context)
                api_client.delete_draft()
                self.context.state = State.NOT_SELECTED
                self.context.last_state = State.DELETE
                break
            elif choice == '2':
                self.context.state = State.SELECTED
                self.context.last_state = State.DELETE
                break
            elif choice == '9':
                self.context.state = State.HELP
                self.context.last_state = State.DELETE
                break
            elif choice == '0':
                exit(0)
            else:
                print("Invalid option, please try again.")
