import inspect
from unittest import mock

import pytest
from requests import JSONDecodeError
from requests.exceptions import ConnectionError as RConnectionError

from wgt import wgt


def test_get_args(monkeypatch: pytest.MonkeyPatch) -> None:
    assert wgt.get_args(["a", "b", "c"]) == ["a", "b", "c"]
    with monkeypatch.context() as m:
        m.setattr("sys.argv", ["/path/to/wgt.py", "a", "b", "c"])
        assert wgt.get_args() == ["a", "b", "c"]

        m.setattr("sys.argv", ["/path/to/python.ext", "-m", "module", "a", "b", "c"])
        assert wgt.get_args() == ["a", "b", "c"]

        m.setattr("sys.argv", ["/path/to/python.ext", "-m", "module"])
        assert wgt.get_args() == []


def test_generate_url_no_args() -> None:
    url = wgt.generate_url([])
    assert url == "https://127.0.0.1:8080/data?json=1#section"


@pytest.mark.parametrize("protocol", ("http://", "https://", "ftp://", "file://"))
def test_generate_url_protocol(protocol: str) -> None:
    url = wgt.generate_url([protocol])
    assert url == f"{protocol}127.0.0.1:8080/data?json=1#section"


@pytest.mark.parametrize("host", ("localhost", "127.0.0.1", "www.youtube.com", "køl.no"))
def test_generate_url_host(host: str) -> None:
    url = wgt.generate_url([host])
    assert url == f"https://{host}:8080/data?json=1#section"


@pytest.mark.parametrize("port", (":8080", ":1", ":65", ":65535"))
def test_generate_url_port(port: str) -> None:
    url = wgt.generate_url([port])
    assert url == f"https://127.0.0.1{port}/data?json=1#section"


def test_generate_url_named_port_service_port(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that :name resolves to {NAME}_SERVICE_PORT environment variable."""
    monkeypatch.setenv("MYSERVICE_SERVICE_PORT", "3000")
    url = wgt.generate_url([":myservice"])
    assert url == "https://127.0.0.1:3000/data?json=1#section"


def test_generate_url_named_port_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that :name falls back to {NAME}_PORT when {NAME}_SERVICE_PORT is not set."""
    monkeypatch.delenv("MYAPP_SERVICE_PORT", raising=False)
    monkeypatch.setenv("MYAPP_PORT", "4000")
    url = wgt.generate_url([":myapp"])
    assert url == "https://127.0.0.1:4000/data?json=1#section"


def test_generate_url_named_port_service_port_takes_precedence(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that {NAME}_SERVICE_PORT takes precedence over {NAME}_PORT."""
    monkeypatch.setenv("API_SERVICE_PORT", "5000")
    monkeypatch.setenv("API_PORT", "6000")
    url = wgt.generate_url([":api"])
    assert url == "https://127.0.0.1:5000/data?json=1#section"


def test_generate_url_named_port_not_found(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture) -> None:
    """Test warning when no matching env var is found for named port."""
    monkeypatch.delenv("UNKNOWN_SERVICE_PORT", raising=False)
    monkeypatch.delenv("UNKNOWN_PORT", raising=False)
    url = wgt.generate_url([":unknown"])
    assert url == "https://127.0.0.1/data?json=1#section"  # No port in URL
    captured = capsys.readouterr()
    assert "UNKNOWN_SERVICE_PORT" in captured.err
    assert "UNKNOWN_PORT" in captured.err


@pytest.mark.parametrize("path", ("/path", "/a/longer/path", "/with/trailing/slash/"))
def test_generate_url_path(path: str) -> None:
    url = wgt.generate_url([path])
    assert url == f"https://127.0.0.1:8080{path.rstrip('/')}?json=1#section"


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("?q=test", "?q=test"),
        ("?start=1656502991&end=1656503004", "?start=1656502991&end=1656503004"),
        ("?q=1,2", "?q=1,2"),
        ("?time=2026-07-29T14:00+0200", "?time=2026-07-29T14:00%2B0200"),
    ],
)
def test_generate_url_query(query: str, expected: str) -> None:
    url = wgt.generate_url([query])
    assert url == f"https://127.0.0.1:8080/data{expected}#section"


@pytest.mark.parametrize(
    ("args", "expected_query"),
    [
        # Two ?param args merged
        (["?a=1", "?b=2"], "?a=1&b=2"),
        # ?param and &param merged
        (["?a=1", "&b=2"], "?a=1&b=2"),
        # Multiple &param args
        (["?a=1", "&b=2", "&c=3"], "?a=1&b=2&c=3"),
        # Timestamps with timezone
        (["?time=2026-07-29T14:00+0200", "?wait=True"], "?time=2026-07-29T14:00%2B0200&wait=True"),
    ],
)
def test_generate_url_multiple_query_params(args: list[str], expected_query: str) -> None:
    url = wgt.generate_url(args)
    assert url == f"https://127.0.0.1:8080/data{expected_query}#section"


@pytest.mark.parametrize("fragment", ("#chapter_one", "#t=1m40s"))
def test_generate_url_fragment(fragment: str) -> None:
    url = wgt.generate_url([fragment])
    assert url == f"https://127.0.0.1:8080/data?json=1{fragment}"


def test_generate_url_combinations() -> None:
    assert wgt.generate_url(["http://", "api", ":443", "/v1"]) == "http://api:443/v1?json=1#section"
    assert wgt.generate_url(["/v1", "?t=now", "#here"]) == "https://127.0.0.1:8080/v1?t=now#here"
    assert wgt.generate_url(["api:443/v1"]) == "https://api:443/v1?json=1#section"
    assert wgt.generate_url(["api/v1"]) == "https://api:8080/v1?json=1#section"
    assert wgt.generate_url(["http://api:443/v1"]) == "http://api:443/v1?json=1#section"
    assert wgt.generate_url(["api ?json=0"]) == "https://api:8080/data?json=0#section"


@mock.patch("requests.get", lambda *_, **__: mock.Mock(json=lambda: {"data": [1, 2, 3]}))
def test_fetch_and_print_json(capsys: pytest.CaptureFixture) -> None:
    wgt.fetch_and_print("http://some.url/returning/json")
    captured = capsys.readouterr()
    assert (
        inspect.cleandoc(
            """
    {
      "data": [
        1,
        2,
        3
      ]
    }
    """
        )
        in captured.out
    )


@mock.patch(
    "requests.get",
    lambda *_, **__: mock.Mock(
        json=mock.Mock(side_effect=JSONDecodeError("", "", 3)), text="<html>Awesome page</html>"
    ),
)
def test_fetch_and_print_text(capsys: pytest.CaptureFixture) -> None:
    wgt.fetch_and_print("http://some.url/returning/text")
    captured = capsys.readouterr()
    assert "<html>Awesome page</html>" in captured.out


@mock.patch("requests.get", mock.Mock(side_effect=RConnectionError("Name or service not known")))
def test_fetch_and_print_exception(capsys: pytest.CaptureFixture) -> None:
    with pytest.raises(SystemExit):
        wgt.fetch_and_print("http://some.invalid.url")
    captured = capsys.readouterr()
    assert "Fetching http://some.invalid.url" in captured.err
    assert "Name or service not known" in captured.err
