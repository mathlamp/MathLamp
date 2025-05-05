from typer.testing import CliRunner
from mathlamp.main import app
from re import match
import pytest

runner = CliRunner()


def test_int():
    result = runner.invoke(app, ["-r", "1+1"])
    assert result.exit_code == 0
    val = result.stdout
    if match(r"[0-9]+\.[0-9]+", val):
        pytest.fail("Value is a float")


def test_float():
    result = runner.invoke(app, ["-r", "1.2+1"])
    assert result.exit_code == 0
    val = result.stdout
    if not match(r"[0-9]+\.[0-9]+", val):
        pytest.fail("Value is a int")


def test_list():
    result = runner.invoke(app, ["-r", "[1,2,3]"])
    assert result.exit_code == 0
    assert result.stdout.strip() == "[1, 2, 3]"


def test_dict():
    result = runner.invoke(app, ["-r", '{"foo":"baz","test":1}'])
    assert result.exit_code == 0
    assert result.stdout.strip() == "{'foo': 'baz', 'test': 1}"
