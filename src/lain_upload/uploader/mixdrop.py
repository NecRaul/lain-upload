from .base import BaseUploader


class MixdropUploader(BaseUploader):
    def __init__(self, file_path, auth=""):
        self.file_path = file_path
        self.auth = auth
        self.file_max_size = 100 * 1000 * 1000 * 1000
        self.file_max_size_str = "100GB"
        self.http_method = "POST"
        self.api_endpoint = "https://ul.mixdrop.ag/api"

    def _build_fields(self, file_name, file):
        try:
            email, key = self.auth.split(":", 1)
        except ValueError as e:
            raise ValueError(
                "Mixdrop uploads require authentication!\nFormat: --auth email:api_key"
            ) from e
        return {
            "file": (file_name, file),
            "email": email,
            "key": key,
        }

    @staticmethod
    def _extract_url(response):
        return f"{response.json()['result']['url']}"
