import filecmp

import click

from obfuscator import cli, examples


def test_cli_obfuscate_passthrough(cli_runner, tmp_path, c_file):
    tmp_path.mkdir(exist_ok=True)
    new_name = f"{c_file.stem}_obfuscated{c_file.suffix}"
    output_file = tmp_path / new_name
    result = cli_runner.invoke(
        cli.app,
        [
            "obfuscate",
            str(c_file.resolve()),
            "--output-file",
            str(output_file),
        ],
    )
    assert result.exit_code == 0
    assert filecmp.cmp(c_file, output_file)


def test_cli_no_output_path(cli_runner, c_file):
    result = cli_runner.invoke(
        cli.app,
        ["obfuscate", str(c_file.resolve())],
    )
    assert result.exit_code == 0
    assert c_file.read_text() in result.stdout


def test_check_path_on_tmp_path(tmp_path):
    tmp_path.mkdir(exist_ok=True)
    try:
        cli.check_path(tmp_path)
    except click.exceptions.Abort:
        assert False


def test_check_path_on_nonexistent_path(tmp_path):
    try:
        cli.check_path(tmp_path / "non_existent_path")
    except click.exceptions.Abort:
        assert True
        return
    assert False


def test_obfuscate_run(
    cli_runner,
):
    pi_path = examples.available_examples()["pi.c"]["path"]
    result = cli_runner.invoke(
        cli.app,
        ["obfuscate", str(pi_path), "5"],
    )
    assert result.exit_code == 0
    assert ">> Results:" in result.stdout


def test_demo(cli_runner):
    result = cli_runner.invoke(
        cli.app,
        ["demo", "pi.c", "5"],
    )
    assert result.exit_code == 0
    assert ">> Results:" in result.stdout


def test_parser(cli_runner):
    result = cli_runner.invoke(
        cli.app,
        ["parser", "--show-ast"],
    )
    assert result.exit_code == 0
    assert "pi_approx" in result.stdout
