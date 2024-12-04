import os


def pytest_configure() -> None:
    os.environ["WGT_DEFAULT_PROTOCOL"] = "https://"
    os.environ["WGT_DEFAULT_HOST"] = "127.0.0.1"
    os.environ["WGT_DEFAULT_PORT"] = ":8080"
    os.environ["WGT_DEFAULT_PATH"] = "/data"
    os.environ["WGT_DEFAULT_QUERY"] = "?json=1"
    os.environ["WGT_DEFAULT_FRAGMENT"] = "#section"
    os.environ["WGT_DRY_RUN"] = "true"
