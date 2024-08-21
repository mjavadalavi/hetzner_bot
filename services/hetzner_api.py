import requests
from config import HETZNER_API_KEY

BASE_URL = "https://api.hetzner.cloud/v1"


def get_headers():
    return {"Authorization": f"Bearer {HETZNER_API_KEY}"}


def get_server_list(country):
    response = requests.get(f"{BASE_URL}/servers", headers=get_headers())
    servers = response.json()["servers"]
    return [server for server in servers if server["datacenter"]["location"]["country"] == country]


def create_server(user, server_details):
    data = {
        "name": f"user_{user.id}_server",
        "server_type": server_details["type"],
        "image": server_details["os"],
        "location": server_details["location"],
    }
    response = requests.post(f"{BASE_URL}/servers", headers=get_headers(), json=data)
    return response.json()["server"]


def delete_server(server_id):
    response = requests.delete(f"{BASE_URL}/servers/{server_id}", headers=get_headers())
    return response.status_code == 204


def reboot_server(server_id):
    response = requests.post(f"{BASE_URL}/servers/{server_id}/actions/reboot", headers=get_headers())
    return response.json()["action"]


def change_server_password(server_id):
    response = requests.post(f"{BASE_URL}/servers/{server_id}/actions/reset_password", headers=get_headers())
    return response.json()["root_password"]


def change_server_os(server_id, new_os):
    data = {"image": new_os}
    response = requests.post(f"{BASE_URL}/servers/{server_id}/actions/rebuild", headers=get_headers(), json=data)
    return response.json()["action"]


def get_server_details(server_id):
    response = requests.get(f"{BASE_URL}/servers/{server_id}", headers=get_headers())
    return response.json()["server"]
