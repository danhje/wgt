from __future__ import annotations

import os
import re
import sys
from pprint import pprint

import requests
from requests import JSONDecodeError
from toolz import compose_left

components = {
    "protocol": os.getenv("WGT_DEFAULT_PROTOCOL", "http://"),
    "host": os.getenv("WGT_DEFAULT_HOST", "localhost"),
    "port": os.getenv("WGT_DEFAULT_PORT", ""),
    "path": os.getenv("WGT_DEFAULT_PATH", "/"),
    "query": os.getenv("WGT_DEFAULT_QUERY", ""),
    "fragment": os.getenv("WGT_DEFAULT_FRAGMENT", ""),
}

pattern = re.compile(
    r"""(?x)
    (?P<protocol>\w{1,9}:\/\/) |
    (?P<port>:\d+) |
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
    except JSONDecodeError:
        print(resp.text)


main = compose_left(get_args, generate_url, fetch_and_print)
