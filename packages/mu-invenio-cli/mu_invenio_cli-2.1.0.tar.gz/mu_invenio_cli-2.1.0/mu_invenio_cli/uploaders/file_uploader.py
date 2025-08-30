#
# Copyright (C) 2025 Masaryk University
#
# MU-INVENIO-CLI is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""File uploader implementation for the MU Invenio CLI application."""
import requests

from mu_invenio_cli.uploaders.base_uploader import BaseUploader


class FileUploader(BaseUploader):
    def upload(self, file_path):
        print(f"Uploading file: {file_path}")
        file_name = file_path.split("/")[-1]
        init_data = [{
            "key": file_name
        }]
        init_file = self.init_file(file_name, init_data)
        if not init_file:
            return 0
        print(f"[1/3]: File {file_name} - initialized")
        upload_success = self.upload_content(file_path, file_name)
        if not upload_success:
            return -1
        print(f"[2/3]: File content - uploaded")
        commit_success = self.commit_file(file_name)
        if not commit_success:
            return -1
        print(f"[3/3]: File {file_name} - created")
        return 1

    def upload_content(self, file_path, file_name):
        url = f"{self.base_api_model_url}/{self.context.selected_id}/draft/files/{file_name}/content"
        headers = self.headers
        headers["Content-Type"] = "application/octet-stream"
        try:
            with open(file_path, "rb") as f:
                response = requests.put(url, headers=headers, data=f, verify=False)
            if response.status_code != 200:
                return False
            return True
        except Exception as e:
            print(f"Error uploading file content: {e}")
            return False
