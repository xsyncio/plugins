#!/usr/bin/env python
"""OSINTBuddy plugins server script

This script contains the commands needed to manage an OSINTBuddy Plugins service, which is used by the OSINTBuddy project.

Basic Commands:
    Plugins service command(s):
        `start` : Starts the FastAPI microservice (`ctrl+c` to stop the microservice)
        `lsp` : Start the language server for code completion in the OSINTBuddy app
    Database Command(s):
        `plugin create` : Run the setup wizard for creating new plugin(s)
        `load $GIT_URL` : Load plugin(s) from a remote git repository
"""
import os
from pathlib import Path
import requests
from os import getpid, devnull
from argparse import ArgumentParser, BooleanOptionalAction
import httpx
from pyfiglet import figlet_format
from termcolor import colored
import osintbuddy

# | Find, share, and get help with OSINTBuddy plugins:
# | https://forum.osintbuddy.com/c/plugin-devs/5

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


def _print_server_details():
    print(colored(figlet_format(f"OSINTBuddy plugins", font='smslant'), color="blue"))
    print(colored(APP_INFO.format(
        osintbuddy_version=osintbuddy.__version__,
        pid=getpid(),
    ), color="blue"))
    colored("Created by", color="blue"), colored("jerlendds & friends", color="red")


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
        log_level='debug'
    )


def create_plugin_wizard():
    # TODO: setup prompt process for initializing an osintbuddy plugin(s) project
    pass



entity_url = lambda entity: f"https://raw.githubusercontent.com/jerlendds/osintbuddy-core-plugins/refs/heads/main/plugins/{entity}"

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
]

def load_git_entities():
    if not Path("./plugins").is_dir():
        os.mkdir("./plugins")

    with httpx.Client() as client:
        for e in ENTITIES:
            if Path(f"./plugins/{e}").exists():
                continue
            else:
                data = client.get(f"{entity_url(e)}")
                with open(f"./plugins/{e}", "w") as file:
                    file.write(data.text)
                    file.close()


def load_core():
    print("____________________________________________________________________")
    print("| Loading core entities...")
    load_git_entities()
    print("____________________________________________________________________")
    print("Done!")


commands = {
    "start": start,
    # "plugin create": create_plugin_wizard,
    "init": load_core
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

