import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from lain_upload import cli


class CliTests(unittest.TestCase):
    def test_upload_prints_file_name_and_url(self):
        with tempfile.NamedTemporaryFile(suffix=".txt") as tmp:
            file_path = Path(tmp.name)

            uploader_instance = MagicMock()
            uploader_instance.upload.return_value = "https://example.test/file\n"

            stdout = io.StringIO()
            stderr = io.StringIO()

            with (
                patch(
                    "lain_upload.cli.uploader.CatboxUploader",
                    return_value=uploader_instance,
                ) as uploader_cls,
                patch("sys.argv", ["lain-upload", "--host", "catbox", str(file_path)]),
                patch("sys.stdout", stdout),
                patch("sys.stderr", stderr),
            ):
                cli.main()

            uploader_cls.assert_called_once_with(file_path)
            self.assertIn(
                f"{file_path.name}: https://example.test/file", stdout.getvalue()
            )

    def test_copies_urls_to_clipboard_when_pyperclip_available(self):
        with tempfile.NamedTemporaryFile(suffix=".txt") as tmp:
            file_path = Path(tmp.name)

            uploader_instance = MagicMock()
            uploader_instance.upload.return_value = "https://example.test/file"

            fake_pyperclip = MagicMock()

            with (
                patch(
                    "lain_upload.cli.uploader.CatboxUploader",
                    return_value=uploader_instance,
                ),
                patch("sys.argv", ["lain-upload", "--host", "catbox", str(file_path)]),
                patch.dict("sys.modules", {"pyperclip": fake_pyperclip}),
            ):
                cli.main()

            fake_pyperclip.copy.assert_called_once_with("https://example.test/file")

    def test_passes_supported_auth_option_to_host_uploader(self):
        with tempfile.NamedTemporaryFile(suffix=".txt") as tmp:
            file_path = Path(tmp.name)

            uploader_instance = MagicMock()
            uploader_instance.upload.return_value = "https://example.test/file"

            with (
                patch(
                    "lain_upload.cli.uploader.GofileUploader",
                    return_value=uploader_instance,
                ) as uploader_cls,
                patch(
                    "sys.argv",
                    [
                        "lain-upload",
                        "--host",
                        "gofile",
                        "--auth",
                        "secret-token",
                        str(file_path),
                    ],
                ),
            ):
                cli.main()

            uploader_cls.assert_called_once_with(file_path, auth="secret-token")

    def test_auth_flag_takes_precedence_over_environment_variable(self):
        with tempfile.NamedTemporaryFile(suffix=".txt") as tmp:
            file_path = Path(tmp.name)

            uploader_instance = MagicMock()
            uploader_instance.upload.return_value = "https://example.test/file"

            stderr = io.StringIO()

            with (
                patch(
                    "lain_upload.cli.uploader.GofileUploader",
                    return_value=uploader_instance,
                ) as uploader_cls,
                patch(
                    "sys.argv",
                    [
                        "lain-upload",
                        "--host",
                        "gofile",
                        "--auth",
                        "flag-secret",
                        str(file_path),
                    ],
                ),
                patch.dict("os.environ", {"GOFILE_API_KEY": "env-secret"}, clear=True),
                patch("sys.stderr", stderr),
            ):
                cli.main()

            uploader_cls.assert_called_once_with(file_path, auth="flag-secret")
            self.assertNotIn("GOFILE_API_KEY", stderr.getvalue())
            self.assertNotIn("env-secret", stderr.getvalue())

    def test_reads_auth_from_environment_when_not_provided(self):
        with tempfile.NamedTemporaryFile(suffix=".txt") as tmp:
            file_path = Path(tmp.name)

            uploader_instance = MagicMock()
            uploader_instance.upload.return_value = "https://example.test/file"

            stderr = io.StringIO()

            with (
                patch(
                    "lain_upload.cli.uploader.GofileUploader",
                    return_value=uploader_instance,
                ) as uploader_cls,
                patch("sys.argv", ["lain-upload", "--host", "gofile", str(file_path)]),
                patch.dict("os.environ", {"GOFILE_API_KEY": "env-secret"}, clear=True),
                patch("sys.stderr", stderr),
            ):
                cli.main()

            uploader_cls.assert_called_once_with(file_path, auth="env-secret")
            self.assertIn("GOFILE_API_KEY", stderr.getvalue())
            self.assertIn("env-secret", stderr.getvalue())

    def test_skips_auth_when_environment_variable_missing(self):
        with tempfile.NamedTemporaryFile(suffix=".txt") as tmp:
            file_path = Path(tmp.name)

            uploader_instance = MagicMock()
            uploader_instance.upload.return_value = "https://example.test/file"

            stderr = io.StringIO()

            with (
                patch(
                    "lain_upload.cli.uploader.GofileUploader",
                    return_value=uploader_instance,
                ) as uploader_cls,
                patch("sys.argv", ["lain-upload", "--host", "gofile", str(file_path)]),
                patch.dict("os.environ", {}, clear=True),
                patch("sys.stderr", stderr),
            ):
                cli.main()

            uploader_cls.assert_called_once_with(file_path)
            self.assertNotIn("GOFILE_API_KEY", stderr.getvalue())

    def test_warns_for_unsupported_option(self):
        with tempfile.NamedTemporaryFile(suffix=".txt") as tmp:
            file_path = Path(tmp.name)

            uploader_instance = MagicMock()
            uploader_instance.upload.return_value = "https://example.test/file"

            stderr = io.StringIO()

            with (
                patch(
                    "lain_upload.cli.uploader.CatboxUploader",
                    return_value=uploader_instance,
                ),
                patch(
                    "sys.argv",
                    [
                        "lain-upload",
                        "--host",
                        "catbox",
                        "--expire-after",
                        "12h",
                        str(file_path),
                    ],
                ),
                patch("sys.stderr", stderr),
            ):
                cli.main()

            self.assertIn(
                "Warning: catbox does not support expire_after option, ignoring it",
                stderr.getvalue(),
            )

    def test_deprecated_host_exits_with_message(self):
        stderr = io.StringIO()

        with (
            patch("sys.argv", ["lain-upload", "--host", "pomf", "dummy.txt"]),
            patch("sys.stderr", stderr),
        ):
            with self.assertRaises(SystemExit) as ctx:
                cli.main()

        self.assertEqual(ctx.exception.code, 2)
        self.assertIn("pomf is no longer supported", stderr.getvalue())

    def test_continues_processing_files_after_error(self):
        with tempfile.NamedTemporaryFile(suffix=".txt") as tmp_ok:
            ok_path = Path(tmp_ok.name)
            missing_path = ok_path.with_name("does-not-exist-for-cli-tests.txt")

            ok_uploader = MagicMock()
            ok_uploader.upload.return_value = "https://example.test/ok"

            def build_uploader(file_path, **kwargs):
                if file_path == missing_path:
                    raise FileNotFoundError(file_path)
                return ok_uploader

            stdout = io.StringIO()
            stderr = io.StringIO()

            with (
                patch(
                    "lain_upload.cli.uploader.CatboxUploader",
                    side_effect=build_uploader,
                ),
                patch(
                    "sys.argv",
                    [
                        "lain-upload",
                        "--host",
                        "catbox",
                        str(missing_path),
                        str(ok_path),
                    ],
                ),
                patch("sys.stdout", stdout),
                patch("sys.stderr", stderr),
            ):
                with self.assertRaises(SystemExit) as ctx:
                    cli.main()

            self.assertEqual(ctx.exception.code, 1)
            self.assertIn(f"File not found: {missing_path}", stderr.getvalue())
            self.assertIn(f"{ok_path.name}: https://example.test/ok", stdout.getvalue())

    def test_exits_with_error_when_upload_fails(self):
        with tempfile.NamedTemporaryFile(suffix=".txt") as tmp:
            file_path = Path(tmp.name)

            uploader_instance = MagicMock()
            uploader_instance.upload.side_effect = ValueError("bad upload")

            stderr = io.StringIO()

            with (
                patch(
                    "lain_upload.cli.uploader.CatboxUploader",
                    return_value=uploader_instance,
                ),
                patch("sys.argv", ["lain-upload", "--host", "catbox", str(file_path)]),
                patch("sys.stderr", stderr),
            ):
                with self.assertRaises(SystemExit) as ctx:
                    cli.main()

            self.assertEqual(ctx.exception.code, 1)
            self.assertIn("Value Error: bad upload", stderr.getvalue())

    def test_exits_with_error_on_unexpected_response(self):
        with tempfile.NamedTemporaryFile(suffix=".txt") as tmp:
            file_path = Path(tmp.name)

            uploader_instance = MagicMock()
            uploader_instance.upload.side_effect = KeyError("missing")

            stderr = io.StringIO()

            with (
                patch(
                    "lain_upload.cli.uploader.CatboxUploader",
                    return_value=uploader_instance,
                ),
                patch("sys.argv", ["lain-upload", "--host", "catbox", str(file_path)]),
                patch("sys.stderr", stderr),
            ):
                with self.assertRaises(SystemExit) as ctx:
                    cli.main()

            self.assertEqual(ctx.exception.code, 1)
            self.assertIn("Unexpected server response", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
