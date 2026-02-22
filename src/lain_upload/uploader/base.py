import sys

import requests
from requests_toolbelt import MultipartEncoderMonitor
from requests_toolbelt.multipart.encoder import MultipartEncoder


class BaseUploader:
    def __init__(self, file_path, file_max_size, file_max_size_str, api_endpoint):
        self.file_path = file_path
        self.file_max_size = file_max_size
        self.file_max_size_str = file_max_size_str
        self.api_endpoint = api_endpoint
        self._done_printed = False

    def upload(self):
        self._done_printed = False
        file_path = self._get_file_path()
        with file_path.open("rb") as file:
            fields = self._build_fields(file_path.name, file)
            data = self._build_monitor(fields)
            headers = {
                "Content-Type": data.content_type,
                "User-Agent": "lain-upload/1.19 (https://github.com/NecRaul/lain-upload)",
            }
            headers.update(self._build_headers())
            response = self._upload_impl(data, headers)
        return self._extract_url(response)

    def _build_fields(self, file_name, file):
        raise NotImplementedError

    @staticmethod
    def _extract_url(response):
        raise NotImplementedError

    def _get_file_path(self):
        file_path = self.file_path
        if not self.file_path.is_file():
            raise FileNotFoundError(file_path)
        file_size = file_path.stat().st_size
        if file_size > self.file_max_size:
            raise ValueError(f"{file_path.name} bigger than {self.file_max_size_str}")
        return file_path

    def _build_monitor(self, fields):
        encoder = MultipartEncoder(fields)
        total_bytes = encoder.len
        return MultipartEncoderMonitor(
            encoder, lambda m: self._progress_callback(m.bytes_read, total_bytes)
        )

    def _build_headers(self):
        return {}

    def _upload_impl(self, data, headers):
        response = requests.post(
            url=self.api_endpoint,
            data=data,
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        return response

    def _progress_callback(self, bytes_sent, total_bytes):
        if total_bytes <= 0 or self._done_printed:
            return

        percent = min(100.0, bytes_sent * 100.0 / total_bytes)
        mb_sent = bytes_sent / (1024 * 1024)
        mb_total = total_bytes / (1024 * 1024)

        bar_width = 30
        filled = int(bar_width * percent / 100)
        bar = "#" * filled + "-" * (bar_width - filled)

        print(
            f"\r[{bar}] {percent:6.2f}% {mb_sent:7.1f}/{mb_total:.1f} MiB",
            file=sys.stderr,
            end="",
            flush=True,
        )

        if bytes_sent >= total_bytes:
            print(file=sys.stderr, flush=True)
            self._done_printed = True
