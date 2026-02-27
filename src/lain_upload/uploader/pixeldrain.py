import base64

from .base import BaseUploader


class PixeldrainUploader(BaseUploader):
    def __init__(self, file_path, auth=""):
        self.file_path = file_path
        self.auth = auth
        self.file_max_size = 100 * 1000 * 1000 * 1000
        self.file_max_size_str = "100GB"
        self.http_method = "POST"
        self.api_endpoint = "https://pixeldrain.com/api/file"

    def _build_fields(self, file_name, file):
        return {"file": (file_name, file)}

    @staticmethod
    def _extract_url(response):
        return f"https://pixeldrain.com/u/{response.json()['id']}"

    def _build_headers(self):
        if not self.auth:
            return {}

        token = base64.b64encode(f":{self.auth}".encode()).decode()
        return {"Authorization": f"Basic {token}"}
