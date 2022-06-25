import os


def pytest_configure():
    os.environ["WG_DEFAULT_PROTOCOL"] = "https://"
    os.environ["WG_DEFAULT_HOST"] = "127.0.0.1"
    os.environ["WG_DEFAULT_PORT"] = ":8080"
    os.environ["WG_DEFAULT_PATH"] = "/data"
    os.environ["WG_DEFAULT_QUERY"] = "?json=1"
    os.environ["WG_DEFAULT_FRAGMENT"] = "#section"
    os.environ["WG_DRY_RUN"] = "true"
