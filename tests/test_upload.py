import os
import tempfile
import time
import unittest
from pathlib import Path
from random import choice
from string import ascii_letters
from urllib.parse import urlparse

import requests
from requests.exceptions import ConnectTimeout

from lain_upload.uploader import (
    CatboxUploader,
    FileDitchUploader,
    GofileUploader,
    LitterboxUploader,
    NullUploader,
    PixeldrainUploader,
    PomfUploader,
    UguuUploader,
)


def _generate_random_content(length=64):
    return "".join(choice(ascii_letters) for _ in range(length))


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


class UploadIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.content = _generate_random_content()
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as temp_file:
            temp_file.write(self.content)
            self.file_path = Path(temp_file.name)

    def tearDown(self):
        if self.file_path.exists():
            self.file_path.unlink()

    def _assert_uploaded_url(
        self,
        url,
        expected_prefixes=None,
        expected_domain_suffixes=None,
        verify_access=True,
    ):
        self.assertTrue(url)

        has_prefix_match = bool(expected_prefixes) and any(
            url.startswith(prefix) for prefix in expected_prefixes
        )

        host = (urlparse(url).hostname or "").lower()
        has_domain_suffix_match = bool(expected_domain_suffixes) and any(
            host == suffix.lower().rstrip("/")
            or host.endswith("." + suffix.lower().rstrip("/"))
            for suffix in expected_domain_suffixes
        )

        self.assertTrue(
            has_prefix_match or has_domain_suffix_match,
            f"Unexpected URL format for {url}",
        )

        if not verify_access:
            return

        last_error = None
        for _ in range(5):
            try:
                response = requests.get(
                    url,
                    timeout=30,
                    headers={
                        "User-Agent": "lain-upload-tests/1.18 (https://github.com/NecRaul/lain-upload)"
                    },
                )
                response.raise_for_status()
                return
            except requests.RequestException as error:
                last_error = error
                time.sleep(1)

        self.fail(f"Could not fetch uploaded file from {url}: {last_error}")

    def test_catbox_upload(self):
        try:
            url = CatboxUploader(self.file_path).upload().strip()
        except ConnectTimeout as e:
            self.skipTest(f"Catbox connect timeout: {e}")
        self._assert_uploaded_url(
            url, ("https://files.catbox.moe/", "https://catbox.moe/")
        )

    def test_litterbox_upload(self):
        try:
            url = LitterboxUploader(self.file_path, expire_after="24h").upload().strip()
        except ConnectTimeout as e:
            self.skipTest(f"Litterbox connect timeout: {e}")
        self._assert_uploaded_url(url, ("https://litter.catbox.moe/",))

    def test_pomf_response_parsing_only(self):
        response = _FakeResponse(
            payload={"files": [{"url": "https://pomf2.lain.la/f/example.txt"}]}
        )
        self.assertEqual(
            PomfUploader._extract_url(response), "https://pomf2.lain.la/f/example.txt"
        )

    def test_uguu_upload(self):
        url = UguuUploader(self.file_path).upload().strip()
        self._assert_uploaded_url(url, expected_domain_suffixes=("uguu.se",))

    def test_fileditch_upload(self):
        url = FileDitchUploader(self.file_path).upload().strip()
        self._assert_uploaded_url(
            url,
            ("https://fileditchfiles.me/file.php?f=/",),
            verify_access=False,
        )

    @unittest.skipIf(
        os.getenv("GITHUB_ACTIONS") == "true", "Skipping NullUploader test on GitHub CI"
    )
    def test_null_upload(self):
        url = (
            NullUploader(self.file_path, expire_after="72h", long_filenames=True)
            .upload()
            .strip()
        )
        self._assert_uploaded_url(url, ("https://0x0.st/",))

    def test_gofile_upload(self):
        try:
            url = GofileUploader(self.file_path).upload().strip()
        except ConnectTimeout as e:
            self.skipTest(f"Gofile connect timeout: {e}")
        self._assert_uploaded_url(
            url, ("https://gofile.io/d/", "https://gofile.io/download/")
        )

    def test_pixeldrain_upload(self):
        pixeldrain_auth = os.getenv("PIXELDRAIN_API_KEY")
        self.assertTrue(
            pixeldrain_auth,
            "Set PIXELDRAIN_API_KEY for Pixeldrain integration test",
        )
        url = PixeldrainUploader(self.file_path, auth=pixeldrain_auth).upload().strip()
        self._assert_uploaded_url(url, ("https://pixeldrain.com/u/",))


if __name__ == "__main__":
    unittest.main()
