from .base import BaseUploader


class CatboxUploader(BaseUploader):
    def __init__(self, file_path, auth=""):
        self.file_path = file_path
        self.auth = auth
        self.file_max_size = 200 * 1000 * 1000
        self.file_max_size_str = "200MB"
        self.http_method = "POST"
        self.api_endpoint = "https://catbox.moe/user/api.php"

    def _build_fields(self, file_name, file):
        return {
            "reqtype": "fileupload",
            "userhash": self.auth,
            "fileToUpload": (file_name, file),
        }

    @staticmethod
    def _extract_url(response):
        return response.text
