"""Helper class to list available examples, and locate them."""

from importlib.resources import files
from typing import Any, Dict

from obfuscator import ctools


def available_examples() -> Dict[str, Dict[str, Any]]:
    """Return a list of the available C function example as
    {file_name:{"path", "header"}}

    Returns:
        Dict[str, Dict[pathlib.Path, str]]: _description_
    """
    c_files = (files("obfuscator") / "data/c_function_examples").glob("*.c")
    return {
        c_file.name: {
            "path": c_file.resolve(),
            "header": ctools.get_function_signatures(c_file.read_text())[0],
        }
        for c_file in c_files
    }


def available_example_help() -> str:
    """Generate a string presenting available examples

    Returns:
        str: string presenting available examples
    """
    functions_and_headers = [
        f"{k}: {v['header']}" for k, v in available_examples().items()
    ]
    return "\n\r".join(functions_and_headers)
