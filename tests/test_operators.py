from typer.testing import CliRunner

from mathlamp.main import app

runner = CliRunner()

def test_arthimetic():
    result = runner.invoke(app, ["test_arthimetic.lmp"])
    assert result.exit_code == 0