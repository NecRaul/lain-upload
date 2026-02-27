from .base import BaseUploader


class NullUploader(BaseUploader):
    def __init__(self, file_path, expire_after=None, long_filenames=False):
        self.file_path = file_path
        self.expire_after = expire_after
        self.long_filenames = long_filenames
        self.file_max_size = 512 * 1024 * 1024
        self.file_max_size_str = "512MiB"
        self.http_method = "POST"
        self.api_endpoint = "https://0x0.st"

    def _build_fields(self, file_name, file):
        data = {"file": (file_name, file)}
        if self.expire_after:
            data["expires"] = self._normalize_expire_after(self.expire_after)
        if self.long_filenames:
            data["secret"] = ""

        return data

    @staticmethod
    def _extract_url(response):
        return response.text

    @staticmethod
    def _normalize_expire_after(requested_str):
        requested = int(requested_str[:-1])
        expire_after = min(requested, 24 * 365)
        return f"{expire_after}"
