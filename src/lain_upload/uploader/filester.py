from lain_upload.uploader.base import BaseUploader


class FilesterUploader(BaseUploader):
    def __init__(self, file_path, auth=""):
        self.file_path = file_path
        self.auth = auth
        self.file_max_size = 10 * 1000 * 1000 * 1000
        self.file_max_size_str = "10GB"
        self.http_method = "POST"
        self.api_endpoint = "https://u1.filester.me/api/v1/upload"

    def _build_fields(self, file_name, file):
        return {"file": (file_name, file)}

    @staticmethod
    def _extract_url(response):
        return response.json()["url"]

    def _build_headers(self):
        if not self.auth:
            return {}

        return {"Authorization": f"Bearer {self.auth}"}
