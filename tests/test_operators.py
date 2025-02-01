from typer.testing import CliRunner
from mathlamp.main import app

from random import randrange
from os import remove

import pytest
from jinja2 import Environment, FileSystemLoader

runner = CliRunner()

environment = Environment(loader=FileSystemLoader("templates/"))

@pytest.fixture
def setup():
    print("\nSetting up resources...")
    lines = [
        {"x": randrange(1, 15), "sign": "+", "y": randrange(1, 15)},
        {"x": randrange(1, 15), "sign": "-", "y": randrange(1, 15)},
        {"x": randrange(1, 15), "sign": "*", "y": randrange(1, 15)},
        {"x": randrange(1, 15), "sign": "/", "y": randrange(1, 15)},
        {"x": randrange(1, 15), "sign": "%", "y": randrange(1, 15)}
    ]
    yield lines
    print("\nRemoving tmp file...")
    remove("tmp.lmp")


def test_arthimetic(setup):
    template = environment.get_template("operator.txt")
    with open("tmp.lmp", "w") as f:
        print("\nWriting tmp file...")
        f.write(template.render(lines=setup))
    result = runner.invoke(app, "tmp.lmp")
    content = result.stdout.splitlines()
    assert result.exit_code == 0

    outputs = []
    print("Calculating...")
    for math in setup:
        match math["sign"]:
            case "+":
                outputs.append(math["x"] + math["y"])

            case "-":
                outputs.append(math["x"] - math["y"])

            case "*":
                outputs.append(math["x"] * math["y"])

            case "/":
                outputs.append(math["x"] / math["y"])

            case "%":
                outputs.append(math["x"] % math["y"])
    print("Checking...")
    for c, o in zip(content,outputs):
        assert float(c) == o