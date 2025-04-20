#!/usr/bin/env python
"""OSINTBuddy plugins CLI

This script contains the commands needed to manage an OSINTBuddy Plugins service, which is used by the OSINTBuddy project.

Basic Commands:
    Plugins service command(s):
        `ob start` : Starts the FastAPI microservice (`ctrl+c` to stop the microservice)
        `ob init` : Load the initial osintbuddy entities onto your filesystem
"""
import os, logging, asyncio, json, sys
from types import NoneType
from pathlib import Path
from os import getpid
from argparse import ArgumentParser
import httpx
from pyfiglet import figlet_format
from termcolor import colored
from osintbuddy import Registry, __version__, Use, load_plugins
from osintbuddy.utils.deps import get_driver

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

ENTITIES = [
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
    if not Path("./plugins").is_dir():
        log.info("directory not found, creating ./plugins")
        os.mkdir("./plugins")

    with httpx.Client() as client:
        for entity in ENTITIES:
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



source = {"id":"1125899906842654","data":{"label":"Website","color":"#1D1DB8","icon":"world-www","elements":[{"value":"github.com","icon":"world-www","label":"Domain","type":"text"}]},"position":{"x":5275.072364647034,"y":3488.8488109543805},"transform":"To IP"}

def prepare_run():
    Registry.labels.clear()
    Registry.plugins.clear()
    Registry.ui_labels.clear()
    load_plugins()


async def run_transform(source: str):
    '''
    E.g.
    ob run '{"id":"1125899906842654","data":{"label":"Website","color":"#1D1DB8","icon":"world-www","elements":[{"value":"github.com","icon":"world-www","label":"Domain","type":"text"}]},"position":{"x":5275.072364647034,"y":3488.8488109543805},"transform":"To IP"}'
    '''
    source = json.loads(source)
    transform_type = source.get("transform")

    prepare_run()
    plugin = await Registry.get_plugin(source.get("data").get("label"))
    
    if not isinstance(plugin, NoneType):
        transform_result = await plugin().run_transform(
            transform_type=transform_type,
            entity=source,
            use=Use(get_driver=get_driver)
        )
        print(transform_result)
        return transform_result
    return []


commands = {
    "start": start,
    # "plugin create": create_plugin_wizard,
    "init": init_entities,
    "run": run_transform
    
}

def main():
    parser = ArgumentParser()
    parser.add_argument('command', type=str, nargs="*", help="[CATEGORY (Optional)] [ACTION]")
    parser.add_argument('-t', '--transform', type=str, nargs="*", help="[CATEGORY (Optional)] [ACTION]")
    
    args = parser.parse_args()
    command_fn_key = ' '.join(args.command)
    command = commands.get(command_fn_key)
    if command:
        if "run" in command_fn_key:
            asyncio.run(command(source=args.transform[0]))
        else:
            command()

    else:
        parser.error("Command not recognized")


if __name__ == '__main__':
    main()
