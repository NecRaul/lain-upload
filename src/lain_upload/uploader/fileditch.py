from lain_upload.uploader.base import BaseUploader


class FileDitchUploader(BaseUploader):
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_max_size = 100 * 1000 * 1000 * 1000
        self.file_max_size_str = "100GB"
        self.http_method = "POST"
        self.api_endpoint = "https://new.fileditch.com/upload.php"

    def _build_fields(self, file_name, file):
        return {"file": (file_name, file)}

    @staticmethod
    def _extract_url(response):
        return response.json()["url"]
