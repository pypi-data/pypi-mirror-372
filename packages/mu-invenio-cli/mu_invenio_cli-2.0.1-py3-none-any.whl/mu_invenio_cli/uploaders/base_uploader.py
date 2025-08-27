#
# Copyright (C) 2025 Masaryk University
#
# MU-INVENIO-CLI is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
#
"""Base uploader class for the MU Invenio CLI application."""

import abc

import requests


def get_file_entity(entries, file_name):
    for entry in entries:
        if entry.get("key") == file_name:
            return entry
    return None


class BaseUploader:
    def __init__(self, context):
        self.context = context
        self.base_api_model_url = f"{self.context.config['BASE_API_URL']}/{self.context.config['MODEL']}"
        self.headers = {
            "Authorization": f"Bearer {self.context.config['API_TOKEN']}",
            "Content-Type": "application/json"
        }

    @abc.abstractmethod
    def upload(self, file_path):
        pass

    def init_file(self, file_name, init_data=None):
        init_url = f"{self.base_api_model_url}/{self.context.selected_id}/draft/files"
        try:
            response = requests.post(
                init_url,
                json=init_data,
                headers=self.headers,
                verify=False
            )
            if response.status_code != 201:
                return {}
            entries = response.json()["entries"]
            return get_file_entity(entries, file_name)
        except requests.exceptions.RequestException as e:
            print(f"Error initializing file upload: {e}")
            return {}

    def commit_file(self, file_name):
        commit_url = f"{self.base_api_model_url}/{self.context.selected_id}/draft/files/{file_name}/commit"
        try:
            response = requests.post(
                commit_url,
                json={},
                headers=self.headers,
                verify=False
            )
            if response.status_code != 200:
                return False
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error commiting file: {e}")
            return False
