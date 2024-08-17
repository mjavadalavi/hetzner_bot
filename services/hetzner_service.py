import requests
import logging
from config import Config


class HetznerService:
    BASE_URL = "https://api.hetzner.cloud/v1"
    HEADERS = {
        "Authorization": f"Bearer {Config.HETZNER_API_KEY}",
        "Content-Type": "application/json"
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def list_servers(self):
        """
        لیست تمام سرورهای موجود برای کاربر را از هتزنر دریافت می‌کند.
        """
        try:
            response = self.session.get(f"{self.BASE_URL}/servers")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching servers: {e}")
            return None

    def change_os(self, server_id, new_image, server_name, server_type, location):
        """
        "Change" the OS by deleting the server and creating a new one with a new OS.

        Args:
            server_id (int): ID of the server to delete.
            new_image (str): The new OS image to use.
            server_name (str): The name for the new server.
            server_type (str): The server type (e.g., 'cx11').
            location (str): The location to create the server.

        Returns:
            dict: The new server details.
        """
        # Step 1: Delete the existing server
        success = self.delete_server(server_id)

        if not success:
            return {"error": "Failed to delete the existing server."}

        # Step 2: Create a new server with the new OS image
        new_server = self.create_server(server_name, server_type, new_image, location)

        if new_server:
            return new_server
        else:
            return {"error": "Failed to create the new server with the desired OS."}
    def list_servers_by_location(self, location_id):
        """
        لیست سرورها را براساس مکان (کشور) مشخص شده فیلتر می‌کند.

        Args:
            location_id (str): شناسه مکان انتخاب شده.

        Returns:
            dict: لیست سرورهای فیلتر شده.
        """
        try:
            response = self.session.get(f"{self.BASE_URL}/server_types")
            response.raise_for_status()
            server_types = response.json()
            if location_id is not None:
                filtered_servers = [
                    server_type for server_type in server_types['server_types'] if location_id in server_type['locations']
                ]
                return filtered_servers
            else:
                return server_types
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching server types: {e}")
            return None

    def create_server(self, name, server_type, image, location):
        """
        سرور جدیدی با مشخصات داده شده ایجاد می‌کند.

        Args:
            name (str): نام سرور.
            server_type (str): نوع سرور (به عنوان مثال 'cx11', 'cx21').
            image (str): سیستم عامل (به عنوان مثال 'ubuntu-20.04').
            location (str): مکان سرور (به عنوان مثال 'nbg1', 'fsn1').

        Returns:
            dict: اطلاعات سرور ایجاد شده.
        """
        payload = {
            "name": name,
            "server_type": server_type,
            "image": image,
            "location": location
        }

        try:
            response = self.session.post(f"{self.BASE_URL}/servers", json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error creating server: {e}")
            return None

    def get_server(self, server_id):
        """
        اطلاعات یک سرور خاص را براساس ID سرور برمی‌گرداند.

        Args:
            server_id (int): شناسه سرور.

        Returns:
            dict: اطلاعات سرور.
        """
        try:
            response = self.session.get(f"{self.BASE_URL}/servers/{server_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching server {server_id}: {e}")
            return None

    def delete_server(self, server_id):
        """
        سرور مورد نظر را براساس ID حذف می‌کند.

        Args:
            server_id (int): شناسه سرور.

        Returns:
            bool: موفقیت عملیات حذف.
        """
        try:
            response = self.session.delete(f"{self.BASE_URL}/servers/{server_id}")
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logging.error(f"Error deleting server {server_id}: {e}")
            return False

    def power_on_server(self, server_id):
        """
        سرور را روشن می‌کند.

        Args:
            server_id (int): شناسه سرور.

        Returns:
            dict: نتیجه عملیات روشن کردن سرور.
        """
        try:
            response = self.session.post(f"{self.BASE_URL}/servers/{server_id}/actions/poweron")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error powering on server {server_id}: {e}")
            return None

    def power_off_server(self, server_id):
        """
        سرور را خاموش می‌کند.

        Args:
            server_id (int): شناسه سرور.

        Returns:
            dict: نتیجه عملیات خاموش کردن سرور.
        """
        try:
            response = self.session.post(f"{self.BASE_URL}/servers/{server_id}/actions/poweroff")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error powering off server {server_id}: {e}")
            return None

    def reboot_server(self, server_id):
        """
        سرور را ریبوت می‌کند.

        Args:
            server_id (int): شناسه سرور.

        Returns:
            dict: نتیجه عملیات ریبوت سرور.
        """
        try:
            response = self.session.post(f"{self.BASE_URL}/servers/{server_id}/actions/reboot")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error rebooting server {server_id}: {e}")
            return None

    def reset_password(self, server_id):
        """
        رمز عبور سرور را ریست می‌کند.

        Args:
            server_id (int): شناسه سرور.

        Returns:
            dict: اطلاعات جدید مربوط به رمز عبور.
        """
        try:
            response = self.session.post(f"{self.BASE_URL}/servers/{server_id}/actions/reset_password")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error resetting password for server {server_id}: {e}")
            return None

    def list_images(self):
        """
        دریافت لیست سیستم عامل‌ها (تصاویر) موجود از API هتزنر.

        Returns:
            dict: لیست تصاویر موجود.
        """
        try:
            response = self.session.get(f"{self.BASE_URL}/images")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching images: {e}")
            return None

    def list_locations(self):
        """
        دریافت لیست کشورها (مکان‌ها) از API هتزنر.

        Returns:
            dict: لیست مکان‌ها.
        """
        try:
            response = self.session.get(f"{self.BASE_URL}/locations")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching locations: {e}")
            return None