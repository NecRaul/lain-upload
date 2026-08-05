from lain_upload.uploader.base import BaseUploader


class WaifuVaultUploader(BaseUploader):
    def __init__(
        self, file_path, expire_after=None, long_filenames=False, single_view=False
    ):
        self.file_path = file_path
        self.expire_after = expire_after
        self.long_filenames = long_filenames
        self.single_view = single_view
        self.file_max_size = 2 * 1000 * 1000 * 1000
        self.file_max_size_str = "2GB"
        self.http_method = "PUT"
        self.api_endpoint = "https://waifuvault.moe/rest"

    def _build_fields(self, file_name, file):
        return {"file": (file_name, file)}

    def _build_parameters(self):
        params = {}
        if self.expire_after:
            params["expires"] = self._normalize_expire_after(self.expire_after)
        if self.long_filenames:
            params["hide_filename"] = "true"
        if self.single_view:
            params["one_time_download"] = "true"

        return params

    @staticmethod
    def _extract_url(response):
        return response.json()["url"]

    @staticmethod
    def _normalize_expire_after(requested_str):
        requested = int(requested_str[:-1])
        expire_after = min(requested, 24 * 365)
        return f"{expire_after}h"
