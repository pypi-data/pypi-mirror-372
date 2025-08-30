#
# Copyright (C) 2025 Masaryk University
#
# MU-INVENIO-CLI is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Batch create state for the MU Invenio CLI application."""
from mu_invenio_cli.file_selector import FileSelector
from mu_invenio_cli.services.record_service import RecordService
from mu_invenio_cli.states.state import State


class BatchCreateState:

    def __init__(self, context):
        self.selected = []
        self.context = context

    def handle(self):
        print("Batch draft create")
        while True:
            print("\nOptions:")
            print("  1. Select json files to create drafts from")
            if self.selected:
                print("  2. Create")
            print("  8. Back")
            print("  9. Help")
            print("  0. Exit")
            choice = input("Select option: ").strip()
            if choice == "1":
                self.selected = FileSelector().select_files()
                if not self.selected:
                    print("No files selected.")
                else:
                    print(f"Selected {len(self.selected)} files.")
            elif choice == "2" and self.selected:
                print("Creating drafts from selected files...")
                record_service = RecordService(self.context)
                files_len = len(self.selected)
                for index, file_path in enumerate(self.selected):
                    created = record_service.create_draft_from_file(file_path)
                    if created:
                        print(f"[{index + 1}/{files_len}] - Draft successfully created .")
                    else:
                        print(f"Failed to create draft from {file_path}.")
                print("Batch draft creation completed.")
                self.context.state = State.NOT_SELECTED
                self.context.last_state = State.BATCH_CREATE
                break
            elif choice == "8":
                self.context.state = State.NOT_SELECTED
                self.context.last_state = State.BATCH_CREATE
                break
            elif choice == "9":
                self.context.state = State.HELP
                self.context.last_state = State.BATCH_CREATE
                break
            elif choice == "0":
                print("Exiting the CLI application.")
                exit(0)
