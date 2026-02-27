import sys

from .base import BaseUploader


class LitterboxUploader(BaseUploader):
    def __init__(self, file_path, expire_after="12h", long_filenames=False):
        self.file_path = file_path
        self.expire_after = expire_after
        self.long_filenames = long_filenames
        self.file_max_size = 1000 * 1000 * 1000
        self.file_max_size_str = "1GB"
        self.http_method = "POST"
        self.api_endpoint = "https://litterbox.catbox.moe/resources/internals/api.php"

    def _build_fields(self, file_name, file):
        return {
            "reqtype": "fileupload",
            "time": self._normalize_expire_after(self.expire_after),
            "fileNameLength": "16" if self.long_filenames else "6",
            "fileToUpload": (file_name, file),
        }

    @staticmethod
    def _extract_url(response):
        return response.text

    @staticmethod
    def _normalize_expire_after(requested_str):
        requested = int(requested_str[:-1])
        supported = sorted({1, 12, 24, 72})
        expire_after = supported[0]
        if requested in supported:
            expire_after = requested
        else:
            expire_after = max(
                [x for x in supported if x < requested], default=expire_after
            )
            print(
                f"Expiration after {requested}h not supported, "
                f"rounding down to {expire_after}h",
                file=sys.stderr,
            )

        return f"{expire_after}h"
