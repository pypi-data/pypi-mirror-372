from typing_extensions import Literal, Any, Union, Dict
from toml import load, dump, TomlDecodeError
from pathlib import Path

__version__ = "0.2.1"
__all__ = [
    "config",
    "get_config",
    "remove_config",
    "init",
    "initsettings",
    "LOCAL",
    "GLOBAL",
    "ALL",
    "HOME",
    "CWD",
]

# Const variables
LOCAL = "local"
GLOBAL = "global"
ALL = "all"
HOME = Path.home()
CWD = Path.cwd()

initsettings = {}


def init(**kwargs):
    """Init configurer settings."""
    global initsettings
    initsettings.update(kwargs)


# Private functions
def _get_config_path(config_type: str) -> Path:
    """Get config file path."""
    config_type = config_type.lower()
    default_paths = {
        GLOBAL: HOME / ".xystudio" / "configurer" / "config.toml",
        LOCAL: CWD / ".xystudio" / "configurer" / "config.toml",
    }
    return Path(
        initsettings.get(f"{config_type}_config_path", default_paths[config_type])
    )


def _parse_config_key(config_name: str) -> list:
    """Parse config key name."""
    case_sensitive = initsettings.get("Case-sensitive", True)
    must_two = initsettings.get("must_two_texts", False)

    processed = config_name if case_sensitive else config_name.lower()

    parts = processed.split(".")

    if must_two and len(parts) < 2:
        raise ValueError("Config name must use 'a.b' format")

    return parts


def _read_config(path: Path) -> dict:
    """Read config file."""
    try:
        with path.open("r", encoding="utf-8") as f:
            return load(f) or {}
    except (FileNotFoundError, TomlDecodeError):
        return {}


def _write_config(path: Path, data: dict):
    """Write config file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        dump(data, f)


def _update_nested(config_dict: dict, keys: list, value: Any):
    """Update nested dict."""
    current = config_dict
    for key in keys[:-1]:
        current = current.setdefault(key, {})
    current[keys[-1]] = value


def config(config_name: str, value: Any, config_type: str = LOCAL):
    """Config a value to config file."""
    config_type = config_type.lower()
    if config_type not in (LOCAL, GLOBAL):
        raise ValueError(f"Invalid config type: {config_type}")

    config_path = _get_config_path(config_type)

    try:
        keys = _parse_config_key(config_name)
    except ValueError as e:
        raise ValueError(f"Invalid config name '{config_name}': {e}") from None

    config_data = _read_config(config_path)
    _update_nested(config_data, keys, value)
    _write_config(config_path, config_data)


def get_config(
    config_name: str,
    default: Any = None,
    config_type: Literal["local", "global", "all"] = LOCAL,
) -> Any:
    """Get a value from config file."""
    local_path = _get_config_path(LOCAL)
    global_path = _get_config_path(GLOBAL)

    configs = {
        LOCAL: _read_config(local_path),
        GLOBAL: _read_config(global_path),
        ALL: {**_read_config(global_path), **_read_config(local_path)},
    }

    target_config = configs.get(config_type.lower())
    if target_config is None:
        raise ValueError(f"Invalid config type: {config_type}")

    if config_name.lower() == ALL:
        return target_config

    try:
        keys = _parse_config_key(config_name)
    except ValueError as e:
        raise ValueError(f"Invalid config name '{config_name}': {e}") from None

    current = target_config
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
        else:
            break
    return current if current is not None else default


def remove_config(config_name: str, config_type: str = LOCAL):
    """Remove a config from config file."""

    config_type = config_type.lower()
    if config_type not in (LOCAL, GLOBAL):
        raise ValueError(f"Invalid config type: {config_type}")

    config_path = _get_config_path(config_type)

    try:
        keys = _parse_config_key(config_name)
    except ValueError as e:
        raise ValueError(f"Invalid config name '{config_name}': {e}") from None

    config_data = _read_config(config_path)

    current = config_data
    for i, key in enumerate(keys):
        if i == len(keys) - 1:
            if key in current:
                del current[key]
                break
        else:
            current = current.get(key, {})

    _write_config(config_path, config_data)


__init__ = init


def _read_init_settings():
    global initsettings
    try:
        with open(
            initsettings.get(
                "local_config_path",
                Path.home() / ".xystudio" / "configurer" / "init_settings.xys",
            ),
            "r",
        ) as f:
            initsettings = load(f)
    except FileNotFoundError:
        pass


def main():
    import argparse

    class globalAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            self.handle_output(parser, namespace, values)

        @staticmethod
        def handle_output(parser, namespace, values):
            setattr(namespace, "_global", values)

    class allAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            self.handle_output(parser, namespace, values)

        @staticmethod
        def handle_output(parser, namespace, values):
            setattr(namespace, "_all", values)

    class localAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            self.handle_output(parser, namespace, values)

        @staticmethod
        def handle_output(parser, namespace, values):
            setattr(namespace, "_local", values)

    parser = argparse.ArgumentParser(description="imgfit commands")
    subparsers = parser.add_subparsers(dest="command", required=False)

    _read_init_settings()

    init_cmd = subparsers.add_parser("init", help="Set the config")
    init_cmd.add_argument("setting")
    init_cmd.add_argument("value")

    set_cmd = subparsers.add_parser("set", help="Set the config")
    set_namespace = set_cmd.add_subparsers(dest="set_namespace", required=True)
    local_config_cmd = set_namespace.add_parser(
        "local",
        help="Config file only in your project.Local config in './.xystudio/pyplus/config.toml'",
    )
    global_config_cmd = set_namespace.add_parser(
        "global",
        help="Config file in all project.Global config in 'Users/Appdata/roaming/xystudio/pyplus/config.toml'",
    )

    local_config_cmd.add_argument("setting", help="Config setting.")
    local_config_cmd.add_argument("value", help="Config value.")

    global_config_cmd.add_argument("setting", help="Config setting.")
    global_config_cmd.add_argument("value", help="Config value.")

    get_conf = subparsers.add_parser("get", help="Get the config.")
    get_conf.add_argument(
        "-l",
        "--local",
        action=localAction,
        nargs="?",
        help="Get the local config in your project.Local config in './.xystudio/pyplus/config.toml'",
    )
    get_conf.add_argument(
        "-g",
        "--global",
        action=globalAction,
        nargs="?",
        help="Output the global config.",
    )
    get_conf.add_argument(
        "-a", "--all", nargs="?", action=allAction, help="Output all the config."
    )

    remove_namespace = subparsers.add_parser(
        "remove", help="Remove the config"
    ).add_subparsers(dest="remove_namespace", required=True)
    local_config_cmd = remove_namespace.add_parser(
        "local",
        help="Config file only in your project.Local config in './.xystudio/pyplus/config.toml'",
    )
    global_config_cmd = remove_namespace.add_parser(
        "global",
        help="Config file in all project.Global config in 'Users/Appdata/roaming/xystudio/pyplus/config.toml'",
    )

    local_config_cmd.add_argument("setting", help="Config setting.")
    global_config_cmd.add_argument("setting", help="Config setting.")

    args = parser.parse_args()

    if args.config_command == "set":
        if args.value.lower() == "true":
            value = True
        elif args.value.lower() == "false":
            value = False
        else:
            value = args.value
        print("Run code again to set the config.")
        config(args.setting, value, args.set_namespace)
    elif args.config_command == "get":
        print(args)
        if hasattr(args, "_local"):
            if args._local is None:
                print(get_config(args.setting, namespace=LOCAL))
            else:
                print(args._local)
                print(get_config(args._local, namespace=LOCAL))
        if hasattr(args, "_global"):
            print(get_config(args.setting, namespace=GLOBAL))
        else:
            print(args._global)
            print(get_config(args._global, namespace=GLOBAL))
        if hasattr(args, "_all"):
            print(get_config(args.setting, namespace=ALL))
        else:
            print(args._all)
            print(get_config(args._all, namespace=ALL))
    elif args.config_command == "remove":
        remove_config(args.setting, args.remove_namespace)
    elif args.config_command == "init":
        initsettings[args.setting] = args.value


if __name__ == "__main__":
    main()
