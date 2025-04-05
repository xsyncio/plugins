#!/usr/bin/env python
"""OSINTBuddy plugins CLI

This script contains the commands needed to manage an OSINTBuddy Plugins service, which is used by the OSINTBuddy project.

Basic Commands:
    Plugins service command(s):
        `ob start` : Starts the FastAPI microservice (`ctrl+c` to stop the microservice)
        `ob init` : Load the initial osintbuddy entities onto your filesystem
"""
import os, logging
from pathlib import Path
from os import getpid
from argparse import ArgumentParser
import httpx
from pyfiglet import figlet_format
from termcolor import colored
import osintbuddy


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
        osintbuddy_version=osintbuddy.__version__,
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
        workers=4,
        port=42562,
        headers=[('server', f"OSINTBuddy")],
        log_level='info'
    )

def load_git_entities():
    if not Path("./plugins").is_dir():
        log.info("directory does not exist, creating ./plugins")
        os.mkdir("./plugins")

    with httpx.Client() as client:
        for entity in ENTITIES:
            log.info(f"loading osintbuddy entity: {entity}")
            if Path(f"./plugins/{entity}").exists():
                continue
            else:
                data = client.get(f"https://raw.githubusercontent.com/jerlendds/osintbuddy-core-plugins/refs/heads/main/plugins/{entity}")
                with open(f"./plugins/{entity}", "w") as file:
                    file.write(data.text)
                    file.close()


def init_entities():
    print("____________________________________________________________________")
    log.info("| Loading osintbuddy entities...")
    load_git_entities()
    print("____________________________________________________________________")
    log.info("Initial entities loaded!")


commands = {
    "start": start,
    # "plugin create": create_plugin_wizard,
    "init": init_entities
}

def main():
    parser = ArgumentParser()
    parser.add_argument('command', type=str, nargs="*", help="[CATEGORY (Optional)] [ACTION]")
    
    args = parser.parse_args()
    command = commands.get(' '.join(args.command))

    if command:
        command()
    else:
        parser.error("Command not recognized")


if __name__ == '__main__':
    main()
