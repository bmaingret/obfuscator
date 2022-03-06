"""Typer application of the obfuscator."""

import importlib
import pathlib
import tempfile
from enum import Enum
from typing import Any, List, Optional

import typer

from obfuscator import Obfuscator, cparser, ctools, examples

app = typer.Typer(help="C Code Obfuscator")


class ObfuscatorLevel(Enum):
    """Defines level of obfuscation and associated Obfuscator class to be used
    through the cli."""

    PassthroughObfuscator = 0
    HarderToRead = 5
    ReplacementObfuscator = 10

    def __str__(self):
        return f"Level ({self.value}) uses ({self.name})"

    @classmethod
    def describe(cls) -> str:
        """Returns a string representation of the enum."""
        return "\n\r".join([str(e) for e in cls])


def get_obfuscator_from_level(obfuscator_level: ObfuscatorLevel) -> Obfuscator:
    """Helper that return the correct Obfuscator class based on the obfuscation
    level.

    Args:
        obfuscator_level (ObfuscatorLevel): Level of obfuscation

    Returns:
        Obfuscator: Corresponding class (not instantiated)
    """
    module = importlib.import_module("obfuscator")
    class_ = getattr(module, obfuscator_level.name)
    return class_


def check_path(path: pathlib.Path):
    """Check that a path exists and output to the console if not.

    Args:
        path (pathlib.Path): (relative) path to check

    Raises:
        typer.Abort: Exit the cli application
    """
    if not path.exists():
        typer.echo(f"Trouble finding path ({path.resolve()})")
        raise typer.Abort()


def obfuscate_at_level(
    level: int, source: str, output_file: pathlib.Path = None
) -> str:
    """Get the corresponding obfuscator, obfuscate code, and output result to
    terminal or file accordingly,
    and return obfuscated code.

    Args:
        level (int): level passed as argument
        source (str): source code
        output_file (pathlib.Path, optional): Path to output file.
        Defaults to None.

    Returns:
        str: obfuscated code.
    """
    typer.echo(f">> {ObfuscatorLevel(level)}\r\n")
    obfuscator_engine = get_obfuscator_from_level(ObfuscatorLevel(level))
    obfuscated = obfuscator_engine().obfuscate(source)
    if output_file is None:
        typer.echo(obfuscated)
        typer.echo("\n\r")
    else:
        check_path(output_file.parent)
        output_file.write_text(obfuscated)
    return obfuscated


def run_function(name: str, source: str, args: Any) -> None:
    """Run a C function based on its C code. The function name must be the one
    defined in the source code. Args must correspond to the signature of the
    function.

    Args:
        name (str): name of the C function
        source (str): source code of the function
        (including #include statements)
        args (Any): Arguments to pass to the C function
    """
    typer.echo(f">> Run {name} with args ({args})")
    with tempfile.TemporaryDirectory() as temp_dir:
        runner = ctools.Runner(pathlib.Path(temp_dir))
        res = runner.compile_and_run("test", source, *args)
        typer.echo(f">> Results: {res} \n\r")


OBFUSCATE_LEVEL_HELP = f"""
\b
Specify the level of obfuscation.
Available:
{ObfuscatorLevel.describe()}
\r\n
"""


@app.command()
def obfuscate(
    c_file: pathlib.Path = typer.Argument(
        ..., help="Path to a C file that you want to obfuscate"
    ),
    args: Optional[List[int]] = typer.Argument(
        None, help="Specify the arguments to pass to the function."
    ),
    level: Optional[int] = typer.Option(
        0,
        "--level",
        "-l",
        help=OBFUSCATE_LEVEL_HELP,
    ),
    output_file: Optional[pathlib.Path] = typer.Option(
        None, help="Specify a directory to save the obfuscated code."
    ),
):
    """Obfuscate passed c_file (as path). If ARGS are passed to the command,
    the function will be ran before and after obfuscation using passed
    arguments.

    If --output-file is not used, obfuscated code will output in terminal.
    """
    check_path(c_file)
    source = c_file.read_text()
    obfuscated = obfuscate_at_level(level, source, output_file)
    if args:
        run_function("original", source, args)
        run_function("obfuscated", obfuscated, args)


@app.command()
def demo(
    function: str = typer.Argument(
        "sum42.c",
        help=f"""Specify the test function to use.\r\n
Available functions:\r\n
{examples.available_example_help()}\r\n""",
    ),
    args: Optional[List[int]] = typer.Argument(
        None, help="Specify the arguments to pass to the function."
    ),
):
    """Run test function through available obfuscator, print resulting
     obfuscated code
    and run the function using the passed arguments if any. When passing
    arguments, the example name MUST be passed to the command."""

    source = examples.available_examples()[function]["path"].read_text()

    for level in ObfuscatorLevel:
        obfuscated = obfuscate_at_level(level, source)
        if args:
            run_function(f"obfuscated level {level}", obfuscated, args)

    if not args:
        typer.echo(
            "If you want to have the function run, please pass arguments \
            according to function signature to the command"
        )


@app.command()
def parser(
    show_ast: Optional[bool] = typer.Option(
        False, "--show-ast", help="Additionnaly show AST for the test function"
    )
):
    """Simply show identified function applying cpyparser to a test function."""
    example = examples.available_examples()["pi.c"]["path"]
    typer.echo(cparser.show_func_defs(example))

    if show_ast:
        typer.echo(cparser.show_ast(example))


if __name__ == "__main__":
    app()  # pragma: no cover
