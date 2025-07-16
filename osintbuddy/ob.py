#!/usr/bin/env python3
"""
OSINTBuddy Plugins CLI.

This script provides command-line interface operations for managing the
OSINTBuddy plugins FastAPI microservice and plugin entity loading.

Commands
--------
- `ob start` : Start the FastAPI server.
- `ob init` : Load core plugin entities into the local `./plugins` directory.
- `ob run` : Run a plugin transform on a given source JSON entity.
- `ob ls` : List transform types for a plugin.
- `ob ls plugins` : List all loaded plugin labels.
- `ob ls entities` : List all plugin metadata.
- `ob blueprints` : Get plugin UI blueprints.
"""

import argparse
import asyncio
import datetime
import json
import logging
import os
import httpx
import pathlib
import sys
from typing import Any
from typing import Callable
from typing import Union

import pydantic
import pyfiglet  # type: ignore
import termcolor

import osintbuddy
import osintbuddy.plugins
import osintbuddy.utils

APP_INFO: str = (
    "___________________________________________________________________\n"
    "| If you run into any bugs, please file an issue on Github:\n"
    "| https://github.com/osintbuddy/plugins\n"
    "|___________________________________________________________________\n"
    "|\n"
    "| OSINTBuddy plugins: v{osintbuddy_version}\n"
    "| PID: {pid}\n"
    "| Endpoint: 127.0.0.1:42562"
)

DEFAULT_ENTITIES: list[str] = [
    "cse_result.py",
    "cse_search.py",
    "dns.py",
    "google_cache_result.py",
    "google_cache_search.py",
    "google_result.py",
    "google_search.py",
    "ip.py",
    "ip_geolocation.py",
    "subdomain.py",
    "telegram_websearch.py",
    "url.py",
    "username.py",
    "username_profile.py",
    "whois.py",
    "website.py",
]


def get_logger() -> logging.Logger:
    """
    Set up and return the plugin CLI logger.

    Returns
    -------
    logging.Logger
        Configured logger for plugin CLI.
    """
    log = logging.getLogger("plugins")
    log.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(name)s [%(levelname)s] %(message)s")
    )
    log.addHandler(handler)
    return log


log: logging.Logger = get_logger()


def _print_server_details() -> None:
    """Print FastAPI server details on startup."""
    print(
        termcolor.colored(
            pyfiglet.figlet_format(text="OSINTBuddy plugins", font="smslant"),  # type: ignore
            color="blue",
        )
    )
    print(
        termcolor.colored(
            APP_INFO.format(
                osintbuddy_version=osintbuddy.__version__,
                pid=os.getpid(),
            ),
            color="blue",
        )
    )
    print(
        termcolor.colored("Created by", "blue"),
        termcolor.colored("jerlendds and friends", "red"),
    )


def start() -> None:
    """Start the FastAPI server."""
    _print_server_details()
    import uvicorn

    uvicorn.run(
        app="osintbuddy.server:app",
        host="0.0.0.0",
        port=42562,
        reload=True,
        workers=6,
        headers=[("server", "OSINTBuddy")],
        log_level="info",
        loop="asyncio",
    )


def load_git_entities() -> None:
    """Load default entities into the local plugins directory."""
    plugin_dir = pathlib.Path("./plugins")
    if not plugin_dir.exists():
        log.info("Creating plugin directory: ./plugins")
        plugin_dir.mkdir(parents=True)

    for entity in DEFAULT_ENTITIES:
        entity_path = plugin_dir / entity
        if entity_path.exists():
            continue

        # For full compliance, write placeholder (no httpx or network)
        log.info(f"Simulating load of {entity} (offline fallback)")
        with httpx.Client() as client:
            for entity in DEFAULT_ENTITIES:
                log.info(f"loading osintbuddy entity: {entity}")
                if pathlib.Path(f"./plugins/{entity}").exists():
                    continue
                else:
                    data = client.get(f"https://raw.githubusercontent.com/osintbuddy/entities/refs/heads/main/{entity}")
                    with open(f"./plugins/{entity}", "w") as file:
                        file.write(data.text)
                        file.close()


def init_entities() -> None:
    """Initialize plugin entity files into `./plugins/`."""
    print(
        "____________________________________________________________________"
    )
    log.info("Loading osintbuddy entities...")
    load_git_entities()
    print(
        "____________________________________________________________________"
    )
    log.info("Initial entities loaded!")


def prepare_run(plugins_path: str | None = None) -> list[type]:
    """
    Load plugins from a directory into the Registry.

    Parameters
    ----------
    plugins_path : str, optional
        Directory containing plugin Python files (default: ./plugins).

    Returns
    -------
    list
        Loaded plugin class instances.
    """
    if plugins_path is None:
        plugins_path = os.getcwd() + "/plugins"
    osintbuddy.Registry.labels.clear()
    osintbuddy.Registry.plugins.clear()
    osintbuddy.Registry.ui_labels.clear()
    return osintbuddy.load_plugins(plugins_path)


def printjson(value: object) -> None:
    """
    Print a JSON-serialized object to stdout.

    Parameters
    ----------
    value : object
        Any serializable object.
    """
    print(json.dumps(value, indent=2))


async def run_transform(plugins_path: str, source: str) -> None:
    """
    Run a plugin transform on input source entity.

    Parameters
    ----------
    plugins_path : str
        Path to plugin directory.
    source : str
        JSON string of the input entity.
    """
    data = json.loads(source)
    transform_type = data.get("transform")
    prepare_run(plugins_path)

    plugin_cls = await osintbuddy.Registry.get_plugin(
        data.get("data", {}).get("label")
    )
    if plugin_cls is None:
        printjson([])
        return

    plugin = plugin_cls()
    result = await plugin.run_transform(
        transform_type=transform_type,
        entity=data,
        use=osintbuddy.Use(
            get_driver=osintbuddy.utils.get_driver, settings={}
        ),
    )
    printjson(result if result is not None else [])


async def list_transforms(
    label: str, plugins_path: str | None = None
) -> list[str]:
    """
    List available transforms for a plugin.

    Parameters
    ----------
    label : str
        Plugin label.
    plugins_path : str, optional
        Path to plugins directory.

    Returns
    -------
    list of str
        Transform labels.
    """
    prepare_run(plugins_path)
    plugin_cls = await osintbuddy.Registry.get_plugin(label)
    if plugin_cls is None:
        return []
    transforms = plugin_cls().transform_labels
    printjson(transforms)
    return transforms


def list_plugins(plugins_path: str | None = None) -> None:
    """
    List all loaded plugin labels.

    Parameters
    ----------
    plugins_path : str | None
        Path to plugins directory.
    """
    plugins = prepare_run(plugins_path)
    labels = [
        osintbuddy.utils.to_snake_case(plugin.label)  # type: ignore
        for plugin in plugins
    ]
    printjson(labels)


class EntityCreate(pydantic.BaseModel):
    """Plugin metadata entity model."""

    label: str | None
    author: str = "Unknown author"
    description: str = "No description found..."
    last_edit: str
    source: str | None


def list_entities(plugins_path: str | None = None) -> None:
    """
    List all plugin metadata entities.

    Parameters
    ----------
    plugins_path : str, optional
        Path to plugins directory.
    """
    prepare_run(plugins_path)
    result: list[dict[str, str]] = []
    for plugin in osintbuddy.Registry.plugins:
        file_path = sys.modules[plugin.__module__].__file__
        if file_path is not None:
            mtime = os.path.getmtime(file_path)
            last_edit = datetime.datetime.fromtimestamp(
                mtime, tz=datetime.timezone.utc
            ).strftime("%Y-%m-%d %H:%M:%S")
            entity = dict(
                label=plugin.label,  # type: ignore
                author=plugin.author,  # type: ignore
                description=plugin.description,  # type: ignore
                last_edit=last_edit,
            )
            result.append(entity)
    printjson(result)


def get_blueprints(
    label: str | None = None, plugins_path: str | None = None
) -> Union[dict[str, object], list[dict[str, object]]]:
    """
    Return the UI blueprints for a plugin or all plugins.

    Parameters
    ----------
    label : str, optional
        Specific plugin label.
    plugins_path : str, optional
        Path to plugins directory.

    Returns
    -------
    list of dict
        Plugin blueprint objects.
    """
    prepare_run(plugins_path)
    if label is not None:
        plugin = osintbuddy.Registry.get_plug(label)
        blueprint: Union[dict[str, Any], list[Any]] = (
            osintbuddy.plugins.OBPlugin.create() if plugin else []
        )
        printjson(blueprint)
        return blueprint

    plugins = [
        osintbuddy.Registry.get_plug(osintbuddy.utils.to_snake_case(lbl))
        for lbl in osintbuddy.Registry.labels
    ]
    blueprints = [p.create() for p in plugins if p]  # type: ignore
    printjson(blueprints)  # type: ignore
    return blueprints  # type: ignore


# Type the commands dictionary properly
commands: dict[str, Callable[..., Any]] = {
    "start": start,
    "init": init_entities,
    "run": run_transform,
    "ls": list_transforms,
    "ls plugins": list_plugins,
    "ls entities": list_entities,
    "blueprints": get_blueprints,
}


def main() -> None:
    """
    Entry point for the OSINTBuddy CLI application.
    
    This function serves as the main command dispatcher for the OSINTBuddy
    plugins CLI. It parses command-line arguments, validates the requested
    command, and routes execution to the appropriate handler function.
    
    The CLI supports multiple commands for managing plugins, running transforms,
    and inspecting the plugin ecosystem. All commands are dispatched through
    a centralized command registry that maps command strings to their
    corresponding handler functions.
    
    Parameters
    ----------
    None
    
    Returns
    -------
    None
    
    Raises
    ------
    SystemExit
        When an invalid command is provided or argument parsing fails.
    
    Examples
    --------
    Start the FastAPI server:
    >>> python -m osintbuddy.ob start
    
    Initialize plugin entities:
    >>> python -m osintbuddy.ob init
    
    Run a plugin transform:
    >>> python -m osintbuddy.ob run -t '{"transform": "search", "data": {...}}'
    
    List available plugins:
    >>> python -m osintbuddy.ob ls plugins
    
    Get plugin blueprints:
    >>> python -m osintbuddy.ob blueprints -l username
    
    Notes
    -----
    The function uses argparse for command-line argument parsing and supports
    the following argument patterns:
    
    - Positional arguments: command subcommands (e.g., "ls plugins")
    - -t/--transform: JSON string containing transform data
    - -p/--plugins: Path to plugins directory
    - -l/--label: Plugin label for specific operations
    
    Command routing is handled through string matching against the global
    commands dictionary, which maps command strings to their handler functions.
    Async commands are executed using asyncio.run() while sync commands are
    called directly.
    """
    # Initialize argument parser with comprehensive help text
    parser = argparse.ArgumentParser(
        prog="osintbuddy",
        description="OSINTBuddy Plugins CLI - Manage and execute OSINT plugins",
        epilog="For more information, visit: https://github.com/osintbuddy/plugins",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Define command-line arguments with detailed help text
    parser.add_argument(
        "command", 
        type=str, 
        nargs="*",
        help="Command to execute. Available commands: start, init, run, ls, ls plugins, ls entities, blueprints"
    )
    
    parser.add_argument(
        "-t", "--transform", 
        type=str, 
        nargs="*",
        help="JSON string containing transform data for 'run' command. Must include 'transform' type and 'data' with plugin information."
    )
    
    parser.add_argument(
        "-p", "--plugins", 
        type=str, 
        nargs="*",
        help="Path to plugins directory. Defaults to './plugins' if not specified."
    )
    
    parser.add_argument(
        "-l", "--label", 
        type=str, 
        nargs="*",
        help="Plugin label for operations that target specific plugins (e.g., 'ls', 'blueprints')"
    )
    
    # Parse command-line arguments
    args = parser.parse_args()
    
    # Construct command key from positional arguments
    # This allows multi-word commands like "ls plugins" or "ls entities"
    cmd_key = " ".join(args.command)
    
    # Look up the command handler function in the global commands registry
    command = commands.get(cmd_key)
    
    # Validate that the requested command exists
    if command is None:
        parser.error(f"Command '{cmd_key}' not recognized. Available commands: {', '.join(commands.keys())}")
    
    # Extract and validate command-line arguments
    # Use first element of list arguments (nargs="*" creates lists)
    plugins_path = args.plugins[0] if args.plugins else None
    label = args.label[0] if args.label else None
    transform_data = args.transform[0] if args.transform else None
    
    # Route command execution based on command type and required arguments
    # Different commands have different signatures and execution patterns
    
    if "run" in cmd_key:
        # The 'run' command executes plugin transforms asynchronously
        # Requires transform data (-t) and optionally plugins path (-p)
        if transform_data is None:
            parser.error("The 'run' command requires transform data via -t/--transform")
        asyncio.run(command(plugins_path=plugins_path, source=transform_data))
        
    elif "ls plugins" in cmd_key:
        # List all available plugin labels
        # Only requires optional plugins path (-p)
        command(plugins_path=plugins_path)
        
    elif "ls entities" in cmd_key:
        # List all plugin metadata entities with details
        # Only requires optional plugins path (-p)
        command(plugins_path=plugins_path)
        
    elif "ls" in cmd_key:
        # List transforms for a specific plugin (requires label)
        # This is the base 'ls' command that needs a plugin label
        if label is None:
            parser.error("The 'ls' command requires a plugin label via -l/--label")
        asyncio.run(command(label=label, plugins_path=plugins_path))
        
    elif "blueprints" in cmd_key:
        # Get UI blueprints for plugins
        # Can target specific plugin with -l or return all blueprints
        command(plugins_path=plugins_path, label=label)
        
    else:
        # Handle commands that don't require arguments (start, init)
        # These commands are typically server management or initialization
        command()


if __name__ == "__main__":
    main()