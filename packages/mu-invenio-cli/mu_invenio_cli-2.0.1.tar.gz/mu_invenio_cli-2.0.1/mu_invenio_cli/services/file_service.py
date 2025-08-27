#
# Copyright (C) 2025 Masaryk University
#
# MU-INVENIO-CLI is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""File service for handling file uploads in the MU Invenio CLI application."""

import os

import requests

from mu_invenio_cli.file_selector import FileSelector
from mu_invenio_cli.uploaders.file_uploader import FileUploader
from mu_invenio_cli.uploaders.multipart_uploader import MultipartUploader


class FileService:
    def __init__(self, context):
        self.context = context
        self.base_api_model_url = f"{self.context.config['BASE_API_URL']}/{self.context.config['MODEL']}"
        self.headers = {
            "Authorization": f"Bearer {self.context.config['API_TOKEN']}",
            "Content-Type": "application/json"
        }

    def _upload_file(self, file_path):
        if not os.path.isfile(file_path):
            print(f"File does not exist: {file_path}")
            return

        file_size = os.path.getsize(file_path)
        if file_size <= 100 * 1024 * 1024:  # 100MB threshold
            uploaded = FileUploader(self.context).upload(file_path)
        else:
            uploaded = MultipartUploader(self.context).upload(file_path)
        if uploaded < 0:
            print(f"File upload failed: {file_path}")
            deleted = self.delete_file(file_path)
            if not deleted:
                print(f"Failed to clean up after upload failure for {file_path}. Please check the server.")

    def upload_single_file(self):
        file_path = FileSelector().select_file_path()
        if not file_path:
            print("No file selected.")
            return
        self._upload_file(file_path)

    def upload_multiple_files(self):
        file_paths = FileSelector().select_files()
        if not file_paths:
            print("No files selected.")
            return
        for file_path in file_paths:
            self._upload_file(file_path)

    def delete_file(self, file_path):
        file_name = file_path.split("/")[-1]
        delete_url = f"{self.base_api_model_url}/{self.context.selected_id}/draft/files/{file_name}"
        try:
            response = requests.delete(delete_url, headers=self.headers, verify=False)
            if response.status_code != 204:
                print(f"Error deleting file {file_name}: {response.status_code}")
                return False
            print(f"File {file_name} deleted successfully.")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error deleting file {file_name}: {e}")
            return False
