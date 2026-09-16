import requests

from config import API_BASE_URL

class YugiohAPIClient:
    def __init__(self):
        self.base_url = API_BASE_URL

    def get_all_cards(self) -> dict:
        url = f"{self.base_url}/cardinfo.php"

        response = requests.get(url, timeout=30)

        response.raise_for_status()

        return response.json()

    