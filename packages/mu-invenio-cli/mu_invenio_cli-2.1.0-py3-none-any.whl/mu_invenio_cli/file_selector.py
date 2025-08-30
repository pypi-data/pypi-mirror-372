#
# Copyright (C) 2025 Masaryk University
#
# MU-INVENIO-CLI is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""File selector utility using Tkinter for the MU Invenio CLI application."""

import tkinter
from tkinter import filedialog


class FileSelector:
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.withdraw()

    def select_file_path(self):
        file_path = filedialog.askopenfilename()
        return file_path if file_path else None

    def select_files(self):
        file_paths = filedialog.askopenfilenames()
        return file_paths if file_paths else ()
