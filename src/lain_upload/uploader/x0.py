from lain_upload.uploader.base import BaseUploader


class X0Uploader(BaseUploader):
    def __init__(self, file_path, long_filenames=False):
        self.file_path = file_path
        self.long_filenames = long_filenames
        self.file_max_size = 1024 * 1024 * 1024
        self.file_max_size_str = "1GiB"
        self.http_method = "POST"
        self.api_endpoint = "https://x0.at"

    def _build_fields(self, file_name, file):
        data = {"file": (file_name, file)}
        if self.long_filenames:
            data["id_length"] = "24"

        return data

    @staticmethod
    def _extract_url(response):
        return response.text
