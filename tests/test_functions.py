from typer.testing import CliRunner
from mathlamp.main import app

runner = CliRunner()

def test_function():
    result = runner.invoke(app, ["-r", 'func hello() {out("hello")} hello()'])
    assert result.exit_code == 0
    assert "hello" in result.stdout

def test_param_func():
    result = runner.invoke(app, ["-r", "func add(x, y) {out(x + y)} add(1, 1)"])
    assert result.exit_code == 0
    assert "2" in result.stdout