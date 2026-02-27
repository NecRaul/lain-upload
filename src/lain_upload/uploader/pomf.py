from .base import BaseUploader


class PomfUploader(BaseUploader):
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_max_size = 1024 * 1024 * 1024
        self.file_max_size_str = "1GiB"
        self.http_method = "POST"
        self.api_endpoint = "https://pomf.lain.la/upload.php"

    def _build_fields(self, file_name, file):
        return {"files[]": (file_name, file)}

    @staticmethod
    def _extract_url(response):
        return response.json()["files"][0]["url"]
