#!/usr/bin/env python3
"""OSINTBuddy plugins CLI

This script contains the commands needed to manage an OSINTBuddy Plugins service, which is used by the OSINTBuddy project.

Basic Commands:
    Plugins service command(s):
        `ob start` : Starts the FastAPI microservice (`ctrl+c` to stop the microservice)
        `ob init` : Load the initial osintbuddy entities onto your filesystem
"""
import logging, asyncio, json
from argparse import ArgumentParser
import httpx
from pyfiglet import figlet_format
from termcolor import colored
from pydantic import BaseModel
from osintbuddy import Registry, __version__, Use, load_plugins
from osintbuddy.utils import get_driver, to_snake_case

APP_INFO = \
"""___________________________________________________________________
| If you run into any bugs, please file an issue on Github:
| https://github.com/osintbuddy/plugins
|___________________________________________________________________
|
| OSINTBuddy plugins: v{osintbuddy_version}
| PID: {pid}
| Endpoint: 127.0.0.1:42562 
""".rstrip()

DEFAULT_ENTITIES = [
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
    "website.py"
]

def get_logger():
    log = logging.getLogger("plugins")
    log.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(name)s [%(levelname)s] %(message)s')
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    log.addHandler(ch)
    return log

log = get_logger()

def _print_server_details():
    from os import getpid
    print(colored(figlet_format(f"OSINTBuddy plugins", font='smslant'), color="blue"))
    print(colored(APP_INFO.format(
        osintbuddy_version=__version__,
        pid=getpid(),
    ), color="blue"))
    print(colored("Created by", color="blue"), colored("jerlendds and friends", color="red"))


def start():
    _print_server_details()
    import uvicorn
    uvicorn.run(
        "osintbuddy.server:app",
        host="0.0.0.0",
        loop='asyncio',
        reload=True,
        workers=6,
        port=42562,
        headers=[('server', 'OSINTBuddy')],
        log_level='info'
    )

def load_git_entities():
    import os
    from pathlib import Path
    if not Path("./plugins").is_dir():
        log.info("directory not found, creating ./plugins")
        os.mkdir("./plugins")

    with httpx.Client() as client:
        for entity in DEFAULT_ENTITIES:
            log.info(f"loading osintbuddy entity: {entity}")
            if Path(f"./plugins/{entity}").exists():
                continue
            else:
                data = client.get(f"https://raw.githubusercontent.com/osintbuddy/entities/refs/heads/main/{entity}")
                with open(f"./plugins/{entity}", "w") as file:
                    file.write(data.text)
                    file.close()


def init_entities():
    print("____________________________________________________________________")
    log.info("| Loading osintbuddy entities...")
    load_git_entities()
    print("____________________________________________________________________")
    log.info("Initial entities loaded!")


def printjson(value: str):
    print(json.dumps(value))

source = {"id":"1125899906842654","data":{"label":"Website","color":"#1D1DB8","icon":"world-www","elements":[{"value":"github.com","icon":"world-www","label":"Domain","type":"text"}]},"position":{"x":5275.072364647034,"y":3488.8488109543805},"transform":"To IP"}

def prepare_run(plugins_path: str = None):
    import os
    if plugins_path == None:
        plugins_path = os.getcwd() + '/plugins'
    Registry.labels.clear()
    Registry.plugins.clear()
    Registry.ui_labels.clear()
    return load_plugins(plugins_path)


async def run_transform(plugins_path: str, source: str):
    '''
    E.g.
    ob run -t '{serde_json::Value<entity-sent-by-ws-user>}'
    '''
    source = json.loads(source)
    transform_type = source.get("transform")

    prepare_run(plugins_path)
    plugin = await Registry.get_plugin(source.get("data").get("label"))
    if not plugin is None:
        transform_result = await plugin().run_transform(
            transform_type=transform_type,
            entity=source,
            use=Use(get_driver=get_driver, settings={})
        )
        printjson(transform_result)
    else:
        print([])


async def list_transforms(label: str, plugins_path: str = None):
    prepare_run(plugins_path)
    plugin = await Registry.get_plugin(label)
    if plugin is None:
        return []
    transforms = plugin().transform_labels
    printjson(transforms)
    return transforms


def list_plugins(plugins_path: str = None):
    plugins = prepare_run(plugins_path)
    loaded_plugins = [to_snake_case(p.label) for p in plugins]
    printjson(loaded_plugins)


class EntityCreate(BaseModel):
    label: str = None
    author: str = "Unknown author"
    description: str = "No description found..."
    last_edit: str
    source: str | None

def list_entities(plugins_path: str = None):
    import os, sys
    from datetime import datetime
    prepare_run(plugins_path)
    printjson([dict(
        label=plugin.label,
        author=plugin.author,
        description=plugin.description,
        last_edit=datetime.utcfromtimestamp(os.path.getmtime(sys.modules[plugin.__module__].__file__ )).strftime('%Y-%m-%d %H:%M:%S'),
    ) for plugin in Registry.plugins])


def get_blueprints(label: str = None, plugins_path: str = None):
    prepare_run(plugins_path)
    if label is None:
        plugins = [Registry.get_plug(to_snake_case(label)) 
                   for label in Registry.labels]
        blueprints = [p.create() for p in plugins]
        printjson(blueprints)
        return blueprints
    plugin = Registry.get_plug(label)
    blueprint = plugin.create() if plugin else []
    printjson(blueprint)
    return blueprint


commands = {
    "start": start,
    # "plugin create": create_plugin_wizard,
    "init": init_entities,
    "run": run_transform,
    "ls": list_transforms,
    "ls plugins": list_plugins,
    "ls entities": list_entities,
    "blueprints": get_blueprints
}

def main():
    parser = ArgumentParser()
    parser.add_argument('command', type=str, nargs="*", help="[CATEGORY (Optional)] [ACTION]")
    parser.add_argument('-t', '--transform', type=str, nargs="*", help="[CATEGORY (Optional)] [ACTION]")
    parser.add_argument('-p', '--plugins', type=str, nargs="*", help="[CATEGORY (Optional)] [ACTION]")
    parser.add_argument('-l', '--label', type=str, nargs="*", help="[CATEGORY (Optional)] [ACTION]")
    
    args = parser.parse_args()
    cmd_fn_key = ' '.join(args.command)
    command = commands.get(cmd_fn_key)
    if command:
        if "run" in cmd_fn_key:
            asyncio.run(command(plugins_path=args.plugins if args.plugins is None else args.plugins[0], source=args.transform[0]))
        elif "ls plugins" in cmd_fn_key:
             command(plugins_path=args.plugins if args.plugins is None else args.plugins[0])
        elif "ls entities" in cmd_fn_key:
            command(plugins_path=args.plugins if args.plugins is None else args.plugins[0])
        elif "ls" in cmd_fn_key:
            asyncio.run(command(label=args.label if args.label is None else args.label[0], plugins_path=args.plugins if args.plugins is None else args.plugins[0]))
        elif "blueprints" in cmd_fn_key:
            command(plugins_path=args.plugins if args.plugins is None else args.plugins[0], label=args.label if args.label is None else args.label[0])
        else:
            command()

    else:
        parser.error("Command not recognized")


if __name__ == '__main__':
    main()
