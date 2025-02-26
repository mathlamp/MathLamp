from typer.testing import CliRunner
from mathlamp.main import app

runner = CliRunner()


def test_eq():
    result = runner.invoke(app, ["-r", "if (1==1) {1+1}"])
    assert result.exit_code == 0
    assert int(result.stdout.strip()) == 2


def test_ne():
    result = runner.invoke(app, ["-r", "if (1!=2) {1+1}"])
    assert result.exit_code == 0
    assert int(result.stdout.strip()) == 2


def test_lt():
    result = runner.invoke(app, ["-r", "if (1<2) {1+1}"])
    assert result.exit_code == 0
    assert int(result.stdout.strip()) == 2


def test_le():
    result = runner.invoke(app, ["-r", "if (1<=1) {1+1}"])
    assert result.exit_code == 0
    assert int(result.stdout.strip()) == 2


def test_gt():
    result = runner.invoke(app, ["-r", "if (2>1) {1+1}"])
    assert result.exit_code == 0
    assert int(result.stdout.strip()) == 2


def test_ge():
    result = runner.invoke(app, ["-r", "if (1>=1) {1+1}"])
    assert result.exit_code == 0
    assert int(result.stdout.strip()) == 2
