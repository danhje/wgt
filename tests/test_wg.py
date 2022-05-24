from typer.testing import CliRunner

from wg.wg import app

runner = CliRunner()


def test_app():
    result = runner.invoke(app, ["Camila"])
    assert result.exit_code == 0
    assert "Hello Camila" in result.stdout
