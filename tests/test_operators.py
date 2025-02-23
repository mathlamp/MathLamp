from typer.testing import CliRunner
from mathlamp.main import app

from random import randrange
from shutil import rmtree
from math import sqrt
from platform import system
import os

import pytest
from jinja2 import Environment, FileSystemLoader

runner = CliRunner()

environment = Environment(loader=FileSystemLoader(os.path.abspath("tests/templates")))


@pytest.fixture(scope="session", autouse=True)
def setup():
    directory = "test-temp"
    print("\nSetting up resources...")
    if not os.path.exists(directory):
        os.makedirs(directory)
    yield directory
    print(f"\nRemoving {directory}...")
    if os.path.exists(directory):
        rmtree(directory)


def test_arthimetic(setup):
    lines = [
        {"x": randrange(1, 15), "sign": "+", "y": randrange(1, 15)},
        {"x": randrange(1, 15), "sign": "-", "y": randrange(1, 15)},
        {"x": randrange(1, 15), "sign": "*", "y": randrange(1, 15)},
        {"x": randrange(1, 15), "sign": "/", "y": randrange(1, 15)},
        {"x": randrange(1, 15), "sign": "%", "y": randrange(1, 15)}
    ]
    template = environment.get_template("operator.txt")
    with open(f"{setup}/arthimetic.lmp", "w") as f:
        print("\nWriting tmp file...")
        f.write(template.render(lines=lines))
    result = runner.invoke(app, f"{setup}/arthimetic.lmp")
    content = result.stdout.splitlines()
    assert result.exit_code == 0
    outputs = []
    print("Calculating...")
    for math in lines:
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
    for c, o in zip(content, outputs):
        assert float(c) == o


def test_functions(setup):
    template = environment.get_template("functions.txt")
    context = {
        "root": randrange(1, 13),
        "x": randrange(1, 13),
        "y": randrange(1, 5)
    }
    with open(f"{setup}/functions.lmp", "w") as f:
        print("\nWriting tmp file...")
        f.write(template.render(context))
    result = runner.invoke(app, f"{setup}/functions.lmp")
    content = result.stdout.splitlines()
    print("Checking...")
    assert result.exit_code == 0
    assert float(content[0]) == sqrt(context["root"])
    assert float(content[1]) == context["x"] ** context["y"]