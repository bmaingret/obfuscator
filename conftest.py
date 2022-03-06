"""Pytest configuration. Mainly fixtures."""

from pathlib import Path
import pytest
from typer.testing import CliRunner

from obfuscator import examples

C_FILE_FIXTURE = "c_file"


def pytest_generate_tests(metafunc):
    """Parametrize test with C_FIL_FIXTURE as argument with examples C functions."""
    if C_FILE_FIXTURE in metafunc.fixturenames:
        c_files = examples.available_examples()
        metafunc.parametrize(
            C_FILE_FIXTURE, [c_file["path"] for c_file in c_files.values()]
        )


def pytest_make_parametrize_id(config, val, argname):
    """Make test ID show passed examples C function file name"""
    if argname == C_FILE_FIXTURE:
        return val.name


@pytest.fixture
def cli_runner():
    """Typer CLI Runner"""
    return CliRunner()
