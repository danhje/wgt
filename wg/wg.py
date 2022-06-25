import os
import re
import sys
from pprint import pprint

import requests
from toolz import compose

components = {
    "protocol": os.getenv("WG_DEFAULT_PROTOCOL", "http://"),
    "host": os.getenv("WG_DEFAULT_HOST", "localhost"),
    "port": os.getenv("WG_DEFAULT_PORT", ""),
    "path": os.getenv("WG_DEFAULT_PATH", "/"),
    "query": os.getenv("WG_DEFAULT_QUERY", ""),
    "fragment": os.getenv("WG_DEFAULT_FRAGMENT", ""),
}

pattern = re.compile(
    r"""(?x)
    (?P<protocol>\w{1,9}:\/\/) |
    (?P<port>:([1-9][0-9]{0,3}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])
              (?:($|[^\d]))) |
    (?P<path>(\/[a-zA-Z0-9&%_-]+)+) |
    (?P<query>\?[a-zA-Z0-9&%=_-]+) |
    (?P<fragment>\#[a-zA-Z0-9&=%_-]+) |
    (?P<host>[^\s\/?#:]+) |
"""
)


def get_args(args: list[str] | None = None) -> list[str]:
    if args:
        return args
    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == "-m":
            return args[i + 2 :]
    return args


def generate_url(args: list[str]) -> str:
    found = {}
    for arg in args:
        for match in pattern.finditer(arg):
            found |= {k: v for k, v in match.groupdict().items() if v is not None}
    return "".join((components | found).values())


def fetch_and_print(url: str) -> None:
    print(f"Fetching {url}")
    resp = requests.get(url)
    resp.raise_for_status()
    try:
        pprint(resp.json())
    except ...:
        print(resp.text)


main = compose(get_args, generate_url, fetch_and_print)
