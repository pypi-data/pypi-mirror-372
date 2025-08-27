import requests


class RecordService:
    def __init__(self, context):
        self.context = context
        self.base_api_model_url = f"{self.context.config['BASE_API_URL']}/{self.context.config['MODEL']}"
        self.headers = {
            "Authorization": f"Bearer {self.context.config['API_TOKEN']}",
            "Content-Type": "application/json"
        }

    def create_draft(self):
        create_url = f"{self.base_api_model_url}/"
        try:
            response = requests.post(create_url, json=self.context.create_json_body, headers=self.headers, verify=False)
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
