from .base import BaseUploader


class ShareyUploader(BaseUploader):
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_max_size = 100 * 1000 * 1000 * 1000
        self.file_max_size_str = "100GB"
        self.http_method = "POST"
        self.api_endpoint = "https://sharey.org/api/upload"

    def _build_fields(self, file_name, file):
        return {"files[]": (file_name, file)}

    @staticmethod
    def _extract_url(response):
        return response.json()["urls"][0]
