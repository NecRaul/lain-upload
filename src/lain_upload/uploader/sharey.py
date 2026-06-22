import sys
from datetime import datetime, timedelta, timezone

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
        return {
            "files[]": (file_name, file),
            "expires_at": (
                datetime.now(timezone.utc)
                + timedelta(hours=self._normalize_expire_after(self.expire_after))
            )
            .isoformat(timespec="milliseconds")
            .replace("+00:00", "Z"),
        }

    @staticmethod
    def _extract_url(response):
        return response.json()["urls"][0]

    @staticmethod
    def _normalize_expire_after(requested_str):
        requested = int(requested_str[:-1])
        supported = sorted({1, 24, 168, 720, 2160})
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

        return expire_after
