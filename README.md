# wgt

A simple API testing CLI. Features:
- Minimizes typing through configurable defaults
- Pretty-prints and syntax highlights JSON responses
- Only the actual response body goes to stdout, all other messages goes to stderr, so you can pipe or redirect the response to files or other tools

## Installation

I recommend installing with pipx:

```
pipx install wgt
```

## Usage

Specify only the parts of the URL that isn't part of your defaults. The rest will be filled in from your defaults.

```shell
> wgt /data
Fetching http://localhost/data
{
  "data": "Hello, world!"
}
```

Defaults are changed through environment variables. Let's say you typically expose your APIs on port 8000,
you use the http protocol, and your endpoint is called `data`. You can set these defaults like this:

```shell
> export WGT_DEFAULT_PROTOCOL=http://
> export WGT_DEFAULT_PORT=:8000
> export WGT_DEFAULT_PATH=/data

> wgt
Fetching http://localhost:8000/data
[...]

> wgt ?foo=bar
Fetching http://localhost:8000/data?foo=bar
[...]
```

The table below lists all environment variables and the defaults that will be used if the variable is not set.

| Variable             | Default                                                                          |
|----------------------|----------------------------------------------------------------------------------|
| WGT_DEFAULT_PROTOCOL | http://                                                                          |
| WGT_DEFAULT_HOST     | localhost                                                                        |
| WGT_DEFAULT_PORT     | None, meaning it will be determined by the protocol (80 for http, 443 for https) |
| WGT_DEFAULT_PATH     | /                                                                                |
| WGT_DEFAULT_QUERY    | None                                                                             |
| WGT_DEFAULT_FRAGMENT | None                                                                             |

To store the response in a file, you can use the `>` operator:

```shell
> wgt /data > data.json
```

The message `Fetching http://localhost/data` will be printed to stderr, and therefore not written to the file.
