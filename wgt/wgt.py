from __future__ import annotations

import os
import re
import sys

import requests
import rich
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
    (?P<query>\?[a-zA-Z0-9&,%=_-]+) |
    (?P<fragment>\#[a-zA-Z0-9&=%_-]+) |
    (?P<host>[^\s\/?#:]+) |
"""
)


def eprint(*args, **kwargs) -> None:
    """Print to stderr."""
    print(*args, file=sys.stderr, **kwargs, flush=True)


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
    eprint(f"Fetching {url}")
    try:
        resp = requests.get(url, timeout=10.0)
        resp.raise_for_status()
    except Exception as e:
        msg = getattr(e, "message", str(e))
        if "Name or service not known" in msg:
            msg = "Name or service not known"
        eprint(msg)
        exit(1)
    try:
        rich.print_json(data=resp.json(), highlight=True)
    except requests.JSONDecodeError:
        print(resp.text)


main = compose_left(get_args, generate_url, fetch_and_print)
