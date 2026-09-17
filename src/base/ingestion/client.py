import time

import requests

from config import API_BASE_URL, REQUESTS_PER_SECOND

class YugiohAPIClient:
    def __init__(self):
        self.base_url = API_BASE_URL
        self.min_request_interval = 1 / REQUESTS_PER_SECOND
        self.last_request_time = 0.0

    def _wait_for_rate_limit(self) -> None:
        elapsed = time.monotonic() - self.last_request_time
        wait_time = self.min_request_interval - elapsed

        if wait_time > 0:
            time.sleep(wait_time)

    def get_all_cards(self) -> dict:
        self._wait_for_rate_limit()

        url = f"{self.base_url}/cardinfo.php"

        response = requests.get(url, timeout=30)

        self.last_request_time = time.monotonic()

        response.raise_for_status()

        return response.json()

    