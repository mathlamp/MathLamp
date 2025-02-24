from typer.testing import CliRunner
from mathlamp.main import app

from random import randrange, sample

runner = CliRunner()

def test_int():
    result = runner.invoke(app,["-r", "1+1"])
    assert result.exit_code == 0
    int(result.stdout)

def test_float():
    result = runner.invoke(app,["-r", "1.2+1"])
    assert result.exit_code == 0
    float(result.stdout)

def test_list():
    result = runner.invoke(app, ["-r", "[1,2,3]"])
    assert result.exit_code == 0
    assert result.stdout.strip() == "[1, 2, 3]"

def test_dict():
    result = runner.invoke(app, ["-r", '{"foo":"baz","test":1}'])
    assert result.exit_code == 0
    assert result.stdout.strip() == "{'foo': 'baz', 'test': 1}"