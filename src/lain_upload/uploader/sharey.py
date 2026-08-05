import sys

from lain_upload.uploader.base import BaseUploader


class ShareyUploader(BaseUploader):
    def __init__(self, file_path, expire_after="168h"):
        self.file_path = file_path
        self.expire_after = expire_after
        self.file_max_size = 100 * 1000 * 1000 * 1000
        self.file_max_size_str = "100GB"
        self.http_method = "POST"
        self.api_endpoint = "https://sharey.org/api/upload"

    def _build_fields(self, file_name, file):
        data = {"files[]": (file_name, file)}
        if self.expire_after:
            data["expiry"] = self._normalize_expire_after(self.expire_after)

        return data

    @staticmethod
    def _extract_url(response):
        return response.json()["urls"][0]

    @staticmethod
    def _normalize_expire_after(requested_str):
        requested = int(requested_str[:-1])
        supported = sorted({1, 24, 168, 720, 2160})
        expire_after = max(
            (x for x in supported if x <= requested),
            default=supported[0],
        )
        if expire_after != requested:
            print(
                f"Expiration after {requested}h not supported, "
                f"rounding down to {expire_after}h",
                file=sys.stderr,
            )

        return f"{expire_after // 24}d" if expire_after >= 24 else f"{expire_after}h"
