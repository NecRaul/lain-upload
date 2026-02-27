from .base import BaseUploader


class GofileUploader(BaseUploader):
    def __init__(self, file_path, auth=""):
        self.file_path = file_path
        self.auth = auth
        self.file_max_size = 100 * 1000 * 1000 * 1000
        self.file_max_size_str = "100GB"
        self.http_method = "POST"
        self.api_endpoint = "https://upload.gofile.io/uploadfile"

    def _build_fields(self, file_name, file):
        return {"file": (file_name, file)}

    @staticmethod
    def _extract_url(response):
        return response.json()["data"]["downloadPage"]

    def _build_headers(self):
        if not self.auth:
            return {}

        return {"Authorization": f"Bearer {self.auth}"}
