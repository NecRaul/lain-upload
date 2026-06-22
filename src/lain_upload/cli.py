import argparse
import json
import os
import sys
from pathlib import Path

import requests

from lain_upload import __version__, config, uploader, util


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
        "tempditch": {"class": "TempDitch", "options": {}},
        "0x0": {"class": "Null", "options": {"expire_after", "long_filenames"}},
        "gofile": {"class": "Gofile", "options": {"auth"}},
        "pixeldrain": {"class": "Pixeldrain", "options": {"auth"}},
        "buzzheavier": {"class": "Buzzheavier", "options": {}},
        "mixdrop": {"class": "Mixdrop", "options": {"auth"}},
        "sharey": {"class": "Sharey", "options": {"expire_after"}},
    }
    deprecated_hosts = {
        "pomf": "pomf is no longer supported.\nSee: https://infrablog.lain.la/pomf-announcement",
    }
    parser = argparse.ArgumentParser(
        description="Upload file to various file hosters",
        formatter_class=argparse.HelpFormatter,
        epilog="Example: %(prog)s --host catbox file1.txt file2.jpg file3.webm",
    )
    parser.add_argument("-v", "--version", action="version", version=__version__)
    config_group = parser.add_mutually_exclusive_group()
    config_group.add_argument("--config", help="load configuration from file")
    config_group.add_argument(
        "--no-config", action="store_true", help="ignore configuration file"
    )
    config_group.add_argument(
        "--init-config",
        nargs="?",
        const=None,
        default=argparse.SUPPRESS,
        help="create default configuration file",
    )
    parser.add_argument(
        "--show-config",
        action="store_true",
        help="show effective configuration and exit",
    )
    parser.add_argument(
        "--host",
        nargs="?",
        default=argparse.SUPPRESS,
        choices=[*allowed_hosts.keys(), "all"],
        help="host to use for uploading",
    )
    parser.add_argument(
        "--auth",
        nargs="?",
        default=argparse.SUPPRESS,
        help="authentication information",
    )
    parser.add_argument(
        "--expire-after",
        nargs="?",
        type=util.expire_after_type,
        default=argparse.SUPPRESS,
        help="file expiration in hours (e.g. 1h, 12h, 24h, 72h). "
        "Unsupported values round down to nearest supported",
    )
    parser.add_argument(
        "--long-filenames",
        action="store_true",
        default=argparse.SUPPRESS,
        help="use longer filenames for uploaded files",
    )
    parser.add_argument("file_paths", nargs="*", default=[], help="File path(s)")

    args = parser.parse_args()

    if hasattr(args, "init_config"):
        path = config.save_config(config.DEFAULT_CONFIG, args.init_config)
        print(f"Config created at {path}", file=sys.stderr)
        if args.show_config:
            print(json.dumps(config.DEFAULT_CONFIG, indent=2))
        return

    cfg = config.load_effective_config(path=args.config, no_config=args.no_config)

    if args.show_config:
        print(json.dumps(cfg, indent=2))
        return

    selected_host = getattr(args, "host", None) or cfg.get("default_host", "catbox")

    if selected_host not in allowed_hosts and selected_host != "all":
        parser.error(f"Invalid host in config: {selected_host}")

    if selected_host in deprecated_hosts:
        parser.error(deprecated_hosts[selected_host])

    if not args.file_paths:
        parser.error("no file(s) specified")

    selected_hosts = (
        [host_name for host_name in allowed_hosts if host_name not in deprecated_hosts]
        if selected_host == "all"
        else [selected_host]
    )

    all_options = {opt for host in allowed_hosts.values() for opt in host["options"]}

    uploaded_urls = []
    has_error = False

    for host_name in selected_hosts:
        host_info = allowed_hosts[host_name]

        if not host_info or host_info["class"] is None:
            parser.error(f"Host {host_name} is not supported.")

        host_class_name = f"{host_info['class']}Uploader"
        if not hasattr(uploader, host_class_name):
            continue
        host_class = getattr(uploader, host_class_name)

        host_options = host_info["options"]
        kwargs = config.get_host_options(cfg, host_name)

        if "auth" in host_options:
            cls = host_info.get("class")
            if isinstance(cls, str):
                auth_env_var = f"{cls.upper()}_API_KEY"
            else:
                parser.error(
                    f"Uploader class for host {host_name} is not an instance of str."
                )
            if auth_from_env := os.getenv(auth_env_var):
                kwargs["auth"] = auth_from_env

        for option in all_options:
            if not hasattr(args, option):
                continue
            value = getattr(args, option)
            if option in host_options:
                kwargs[option] = value
            else:
                print(
                    f"Warning: {host_name} does not support {option} option, "
                    f"ignoring it",
                    file=sys.stderr,
                )

        if kwargs.get("auth"):
            print(f"Using {host_info['class']} auth: {kwargs['auth']}", file=sys.stderr)

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
