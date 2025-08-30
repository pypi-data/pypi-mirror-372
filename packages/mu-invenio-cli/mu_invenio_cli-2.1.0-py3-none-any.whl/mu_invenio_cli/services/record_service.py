import json

import requests


class RecordService:
    def __init__(self, context):
        self.context = context
        self.base_api_model_url = f"{self.context.config['BASE_API_URL']}/{self.context.config['MODEL']}"
        self.headers = {
            "Authorization": f"Bearer {self.context.config['API_TOKEN']}",
            "Content-Type": "application/json"
        }

    def create_draft_from_file(self, file_path):
        try:
            with open(file_path, 'r') as f:
                json_body = json.load(f)
        except Exception as e:
            print(f"Failed to load JSON from file: \n     {e}")
            return None
        return self.create_draft(json_body)

    def create_draft(self, json_body):
        create_url = f"{self.base_api_model_url}/"
        try:
            response = requests.post(create_url, json=json_body, headers=self.headers, verify=False)
        except requests.exceptions.RequestException as e:
            print(f"Error creating draft: {e}")
            return None
        if response.status_code == 201:
            print("Draft created successfully.")
        else:
            print(f"Failed to create draft: {response.status_code} - {response.text}")
            return None
        response_json = response.json()
        return response_json

    def create_draft_from_context(self):
        if not self.context.create_json_body:
            print("No JSON body set for draft creation.")
            return None
        return self.create_draft(self.context.create_json_body)

    def get_draft(self, draft_id):
        get_url = f"{self.base_api_model_url}/{draft_id}/draft"
        try:
            response = requests.get(get_url, headers=self.headers, verify=False)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching draft: {e}")
            return None
        if response.status_code == 200:
            print("Draft fetched successfully.")
        else:
            print(f"Failed to fetch draft: {response.status_code} - {response.text}")
            return None
        response_json = response.json()
        return response_json

    def get_user_records(self, query="", page=1):
        list_url = f"{self.context.config['BASE_API_URL']}/user/search/?q={query}&page={page}&size=15"
        try:
            response = requests.get(list_url, headers=self.headers, verify=False)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching drafts: {e}")
            return None
        if response.status_code == 200:
            print("Drafts fetched successfully.")
        else:
            print(f"Failed to fetch drafts on url {list_url}: {response.status_code} - {response.text}")
            return None
        response_json = response.json()
        records = response_json.get('hits', {}).get('hits', [])
        return records

    def delete_draft(self):
        delete_url = f"{self.base_api_model_url}/{self.context.selected_id}/draft"
        try:
            response = requests.delete(delete_url, headers=self.headers, verify=False)
        except requests.exceptions.RequestException as e:
            print(f"Error deleting draft: {e}")
            return False
        if response.status_code == 204:
            print("Draft deleted successfully.")
            return True
        else:
            print(f"Failed to delete draft: {response.status_code} - {response.text}")
            return False
