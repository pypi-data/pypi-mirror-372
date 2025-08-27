from typer.testing import CliRunner

from grem.__main__ import app

runner = CliRunner()


def test_app():
    result = runner.invoke(app)
    assert result.exit_code == 0
    assert 'It works!' in result.stdout
