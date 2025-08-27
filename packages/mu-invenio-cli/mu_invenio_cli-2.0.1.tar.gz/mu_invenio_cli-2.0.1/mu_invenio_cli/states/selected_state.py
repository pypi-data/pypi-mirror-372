#
# Copyright (C) 2025 Masaryk University
#
# MU-INVENIO-CLI is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Selected state for the MU Invenio CLI application.
This state handles the actions when the draft is selected.
"""

from .base_state import BaseState
from .state import State
from ..services.file_service import FileService


class SelectedState(BaseState):
    def handle(self):
        while True:
            print("\nSelected Draft Options:")
            print("  1. Print draft data")
            print("  2. Edit draft - not implemented yet")
            print("  3. Delete draft")
            print("  4. Upload files")
            print("  8. Back to select draft")
            print("  9. Help")
            print("  0. Exit")

            choice = input("Select option: ").strip()
            if choice == '1':
                self.print_create_json_body()
            elif choice == '2':
                print("Editing draft is not implemented yet.")
            elif choice == '3':
                self.context.state = State.DELETE
                self.context.last_state = State.SELECTED
                break
            elif choice == '4':
                FileService(self.context).upload_multiple_files()
                break
            elif choice == '9':
                self.context.state = State.HELP
                self.context.last_state = State.SELECTED
                break
            elif choice == '0':
                exit(0)
            else:
                print("Invalid option, please try again.")
