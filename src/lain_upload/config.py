import copy
import json
import os
import platform
from pathlib import Path

from . import util

CONFIG_NAMESPACE = "necraul"
CONFIG_NAME = "lain-upload.json"

DEFAULT_CONFIG = {
    "default_host": "catbox",
    "hosts": {
        "catbox": {"auth": None},
        "litterbox": {
            "expire_after": "12h",
            "long_filenames": False,
        },
        "pomf": {},
        "uguu": {},
        "fileditch": {},
        "tempditch": {},
        "0x0": {"expire_after": None, "long_filenames": False},
        "gofile": {"auth": None},
        "pixeldrain": {"auth": None},
        "buzzheavier": {},
        "mixdrop": {"auth": None},
        "sharey": {"expire_after": "168h"},
    },
}


def get_default_config_path():
    match platform.system():
        case "Windows":
            base = os.getenv("APPDATA")
            if base:
                config_dir = Path(base)
            else:
                config_dir = Path.home() / "AppData" / "Roaming"
        case "Darwin":
            config_dir = Path.home() / "Library" / "Application Support"
        case "Linux":
            config_dir = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config"))
        case _:
            config_dir = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config"))
    return config_dir / CONFIG_NAMESPACE / CONFIG_NAME


def load_config(path=None):
    if path is None:
        path = get_default_config_path()
    else:
        path = Path(path).expanduser()
    if not path.exists():
        return copy.deepcopy(DEFAULT_CONFIG)
    with path.open("r", encoding="utf-8") as f:
        user_cfg = json.load(f)
    return merge_config(DEFAULT_CONFIG, user_cfg)


def merge_config(base, override):
    result = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merge_config(result[key], value)
        else:
            result[key] = value
    return result


def save_config(cfg, path=None):
    if path is None:
        path = get_default_config_path()
    path = Path(path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
        f.write("\n")
    return path.absolute()


def load_effective_config(path=None, no_config=False):
    if no_config:
        return copy.deepcopy(DEFAULT_CONFIG)
    if path:
        return load_config(path)
    return load_config()


def get_host_options(cfg, host_name):
    options = cfg.get("hosts", {}).get(host_name, {}).copy()
    for key, value in options.items():
        options[key] = validate_option(key, value)
    return options


def validate_option(name, value):
    match name:
        case "expire_after":
            if not value:
                return value
            return util.expire_after_type(value)
        case _:
            return value
