import requests
from config import HETZNER_API_TOKEN

class HetznerService:
    def __init__(self):
        self.headers = {
            'Authorization': f'Bearer {HETZNER_API_TOKEN}',
            'Content-Type': 'application/json'
        }

    def get_countries(self):
        url = 'https://api.hetzner.cloud/v1/locations'
        response = requests.get(url, headers=self.headers)
        return response.json()['locations']

    def get_servers_by_country(self, country):
        url = f'https://api.hetzner.cloud/v1/server_types?location={country}'
        response = requests.get(url, headers=self.headers)
        return response.json()['server_types']

    def create_server(self, user_id, server_type, location):
        url = 'https://api.hetzner.cloud/v1/servers'
        data = {
            "name": f"server-{user_id}",
            "server_type": server_type,
            "location": location
        }
        response = requests.post(url, json=data, headers=self.headers)
        return response.json()
