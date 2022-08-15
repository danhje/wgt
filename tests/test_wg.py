import mock
import pytest
from requests import JSONDecodeError
from requests.exceptions import ConnectionError as RConnectionError

from wgt import wgt


def test_get_args(monkeypatch):
    assert wgt.get_args(["a", "b", "c"]) == ["a", "b", "c"]
    with monkeypatch.context() as m:
        m.setattr("sys.argv", ["/path/to/wgt.py", "a", "b", "c"])
        assert wgt.get_args() == ["a", "b", "c"]

        m.setattr("sys.argv", ["/path/to/python.ext", "-m", "module", "a", "b", "c"])
        assert wgt.get_args() == ["a", "b", "c"]

        m.setattr("sys.argv", ["/path/to/python.ext", "-m", "module"])
        assert wgt.get_args() == []


def test_generate_url_no_args():
    url = wgt.generate_url([])
    assert url == "https://127.0.0.1:8080/data?json=1#section"


@pytest.mark.parametrize("protocol", ("http://", "https://", "ftp://", "file://"))
def test_generate_url_protocol(protocol):
    url = wgt.generate_url([protocol])
    assert url == f"{protocol}127.0.0.1:8080/data?json=1#section"


@pytest.mark.parametrize("host", ("localhost", "127.0.0.1", "www.youtube.com", "køl.no"))
def test_generate_url_host(host):
    url = wgt.generate_url([host])
    assert url == f"https://{host}:8080/data?json=1#section"


@pytest.mark.parametrize("port", (":8080", ":1", ":65", ":65535"))
def test_generate_url_port(port):
    url = wgt.generate_url([port])
    assert url == f"https://127.0.0.1{port}/data?json=1#section"


@pytest.mark.parametrize("path", ("/path", "/a/longer/path", "/with/trailing/slash/"))
def test_generate_url_path(path):
    url = wgt.generate_url([path])
    assert url == f"https://127.0.0.1:8080{path.rstrip('/')}?json=1#section"


@pytest.mark.parametrize("query", ("?q=test", "?start=1656502991&end=1656503004"))
def test_generate_url_query(query):
    url = wgt.generate_url([query])
    assert url == f"https://127.0.0.1:8080/data{query}#section"


@pytest.mark.parametrize("fragment", ("#chapter_one", "#t=1m40s"))
def test_generate_url_fragment(fragment):
    url = wgt.generate_url([fragment])
    assert url == f"https://127.0.0.1:8080/data?json=1{fragment}"


def test_generate_url_combinations():
    assert wgt.generate_url(["http://", "api", ":443", "/v1"]) == "http://api:443/v1?json=1#section"
    assert wgt.generate_url(["/v1", "?t=now", "#here"]) == "https://127.0.0.1:8080/v1?t=now#here"
    assert wgt.generate_url(["api:443/v1"]) == "https://api:443/v1?json=1#section"
    assert wgt.generate_url(["api/v1"]) == "https://api:8080/v1?json=1#section"
    assert wgt.generate_url(["http://api:443/v1"]) == "http://api:443/v1?json=1#section"
    assert wgt.generate_url(["api ?json=0"]) == "https://api:8080/data?json=0#section"


@mock.patch("requests.get", lambda *args: mock.Mock(json=lambda: {"data": [1, 2, 3]}))
def test_fetch_and_print_json(capsys):
    wgt.fetch_and_print("http://danielhjertholm.me")
    captured = capsys.readouterr()
    assert "{'data': [1, 2, 3]}" in captured.out


@mock.patch(
    "requests.get",
    lambda *args: mock.Mock(
        json=mock.Mock(side_effect=JSONDecodeError("", "", 3)), text="<html>Awesome page</html>"
    ),
)
def test_fetch_and_print_text(capsys):
    wgt.fetch_and_print("http://danielhjertholm.me")
    captured = capsys.readouterr()
    assert "<html>Awesome page</html>" in captured.out


@mock.patch("requests.get", mock.Mock(side_effect=RConnectionError("Name or service not known")))
def test_fetch_and_print_exception(capsys):
    with pytest.raises(SystemExit):
        wgt.fetch_and_print("http://some.invalid.url")
    captured = capsys.readouterr()
    assert captured.out == "Fetching http://some.invalid.url\n"
    assert "Name or service not known" in captured.err
