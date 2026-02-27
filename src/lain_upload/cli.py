import argparse
import os
import sys
from pathlib import Path

import requests

from . import uploader, util
from .version import __version__


def main():
    allowed_hosts = {
        "catbox": {"class": "Catbox", "options": {"auth"}},
        "litterbox": {
            "class": "Litterbox",
            "options": {"expire_after", "long_filenames"},
        },
        "pomf": {"class": "Pomf", "options": {}},
        "uguu": {"class": "Uguu", "options": {}},
        "fileditch": {"class": "FileDitch", "options": {}},
        "0x0": {"class": "Null", "options": {"expire_after", "long_filenames"}},
        "gofile": {"class": "Gofile", "options": {"auth"}},
        "pixeldrain": {"class": "Pixeldrain", "options": {"auth"}},
        "buzzheavier": {"class": "Buzzheavier", "options": {}},
    }
    deprecated_hosts = {
        "pomf": "pomf is no longer supported.\nSee: https://infrablog.lain.la/pomf-announcement",
    }
    parser = argparse.ArgumentParser(
        description="Upload file to pomf.lain.la",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog="Example: %(prog)s --host catbox file1.txt file2.jpg file3.webm",
    )
    parser.add_argument("-v", "--version", action="version", version=__version__)
    parser.add_argument(
        "--host",
        nargs="?",
        default="catbox",
        choices=allowed_hosts.keys(),
        help="host to use for uploading",
    )
    parser.add_argument("--auth", nargs="?", help="authentication information")
    parser.add_argument(
        "--expire-after",
        nargs="?",
        type=util.expire_after_type,
        help="file expiration in hours (e.g. 1h, 12h, 24h, 72h). "
        "Unsupported values round down to nearest supported",
    )
    parser.add_argument(
        "--long-filenames",
        nargs="?",
        const=True,
        default=None,
        help="use longer filenames for uploaded files",
    )
    parser.add_argument("file_paths", nargs="+", help="File path(s)")

    args = parser.parse_args()

    if args.host in deprecated_hosts:
        parser.error(deprecated_hosts[args.host])

    host_info = allowed_hosts[args.host]

    if not host_info or host_info["class"] is None:
        parser.error(f"Host {args.host} is not supported.")

    host_class_name = f"{host_info['class']}Uploader"
    if isinstance(host_class_name, str):
        host_class = getattr(uploader, host_class_name)
    else:
        parser.error(f"Uploader class for host {args.host} is invalid.")

    host_options = host_info["options"]
    all_options = {opt for host in allowed_hosts.values() for opt in host["options"]}
    kwargs = {}

    for option in all_options:
        value = getattr(args, option, None)
        if value is None:
            continue
        if option in host_options:
            kwargs[option] = value
        else:
            print(
                f"Warning: {args.host} does not support {option} option, ignoring it",
                file=sys.stderr,
            )

    if "auth" in host_options and "auth" not in kwargs:
        cls = host_info.get("class")
        if isinstance(cls, str):
            auth_env_var = f"{cls.upper()}_API_KEY"
        else:
            parser.error(
                f"Uploader class for host {args.host} is not an instance of str."
            )
        auth_from_env = os.getenv(auth_env_var)
        if auth_from_env:
            print(f"Using {auth_env_var}: {auth_from_env}", file=sys.stderr)
            kwargs["auth"] = auth_from_env

    uploaded_urls = []
    has_error = False

    for file_path_str in args.file_paths:
        try:
            file_path = Path(file_path_str)
            uploader_instance = host_class(file_path, **kwargs)
            url = uploader_instance.upload().strip()
            print(f"{file_path.name}: {url}")
            uploaded_urls.append(url)
        except FileNotFoundError as e:
            print(f"File not found: {e}", file=sys.stderr)
            has_error = True
            continue
        except ValueError as e:
            print(f"Value Error: {e}", file=sys.stderr)
            has_error = True
            continue
        except requests.RequestException as e:
            print(f"Network error: {e}", file=sys.stderr)
            has_error = True
            continue
        except (KeyError, IndexError, TypeError) as e:
            print(f"Unexpected server response: {e}", file=sys.stderr)
            has_error = True
            continue

    if uploaded_urls:
        all_urls = "\n".join(uploaded_urls)
        try:
            import pyperclip

            pyperclip.copy(all_urls)
            print("\nURL(s) copied to clipboard", file=sys.stderr)
        except Exception:
            pass

    if has_error:
        sys.exit(1)
