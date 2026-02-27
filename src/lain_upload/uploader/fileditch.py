from .base import BaseUploader


class FileDitchUploader(BaseUploader):
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_max_size = 15 * 1000 * 1000 * 1000
        self.file_max_size_str = "15GB"
        self.http_method = "POST"
        self.api_endpoint = "https://up1.fileditch.com/upload.php"

    def _build_fields(self, file_name, file):
        return {"files[]": (file_name, file)}

    @staticmethod
    def _extract_url(response):
        return response.json()["files"][0]["url"]
