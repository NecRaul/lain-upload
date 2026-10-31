from lain_upload.uploader.base import BaseUploader


class PoneUploader(BaseUploader):
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_max_size = 1024 * 1024 * 1024
        self.file_max_size_str = "1GiB"
        self.http_method = "POST"
        self.api_endpoint = "https://pone.rs/upload?output=text"

    def _build_fields(self, file_name, file):
        return {"files[]": (file_name, file)}

    @staticmethod
    def _extract_url(response):
        return response.text
