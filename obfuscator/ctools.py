"""Implements helpers to run C code (using CCFI), regex for includes, function
signature, generating #include statement, etc. """

import importlib
import pathlib
import re
import subprocess
import sys
from typing import Any, List

from cffi import FFI


def generate_include_lib_str(lib: str) -> str:
    """Generate an C include statement.

    Example: generate_include_lib_str('stdin.h') -> '#include <stdin.h>

    Args:
        lib (str): library name. Will be used as is in the include.

    Returns:
        str: a C include.
    """
    return f"#include <{lib}>"


def insert_lib(source: str, lib: str) -> str:
    """Add a include statement for the lib if not already present.

    Args:
        source (str): source code
        lib (str): library name. Will be used as is.

    Returns:
        str: source code with added library if needed.
    """
    if is_lib_included(source, lib):
        return source
    source_with_lib = f"{generate_include_lib_str(lib)}\n{source}"
    return source_with_lib


def get_includes(source: str) -> List[str]:
    """Regex the includes of the source code.

    Args:
        source (str): source code

    Returns:
        List[str]: List of included library (ex: ['stdin.h'])
    """
    include_pattern = r"^[^\S\r\n]*\#[^\S\r\n]*include[^\S\r\n]*[\"<]([^\">]+)[\">]\s*"
    compiled_pattern = re.compile(include_pattern, re.M)
    includes = re.findall(compiled_pattern, source)
    return includes


def is_lib_included(source: str, lib: str) -> bool:
    """Check if a library is included in the source code.
        Will check for exact match (i.e. 'stdin' <> 'stdin.h')

    Args:
        source (str): source code
        lib (str): library name

    Returns:
        bool: whether the library is included in the source code.
    """
    return lib in get_includes(source)


def get_function_signatures(source: str) -> List[str]:
    """Return a list of the functions signature present in the source code
    (regex based).
        Signatures will include an ending semi-colon.
    Args:
        source (str): source code

    Returns:
        List[str]: List of signatures, each with an ending semi-colon.
    """
    function_pattern = r"^[^\S\r\n]*((?:[\w\*]+(?: )*?){2,}\([^!@#$+%^;]+?\)(?!\s*;))"
    compiled_pattern = re.compile(function_pattern, re.M)
    functions = re.findall(compiled_pattern, source)
    return [function + ";" for function in functions]


def count_args(function_def: str) -> int:
    """Count a function signature arguments (counts the coma)

    Args:
        function_def (str): function signature

    Returns:
        int: number of arguments (based on comma)
    """
    return function_def.count(",") + 1


def get_function_name(function_signature: str) -> str:
    """Regex the function name from a function signature.

    Args:
        function_signature (str): function signature

    Raises:
        ValueError: If no name is found.

    Returns:
        str: function name
    """
    name_pattern = r"^[^\S\r\n]*(?:([\w\*]+(?: )*?){2,}\([^!@#$+%^;]+?\))"
    compiled_pattern = re.compile(name_pattern, re.M)
    function_name = re.search(compiled_pattern, function_signature)
    if function_name:
        return function_name.group(1)
    raise ValueError(f"Trouble finding function name in ({function_signature})")


def gcc_compile(module: str, source: str, tmp_dir: pathlib.Path) -> str:
    """Run `gcc -c` on the source code and then use `strip` to remove symbol
    table.
    Returns command result. Uses subprocess.

    Args:
        module (str): a module name used for the generated file.
        source (str): compilable source code.
        tmp_dir (pathlib.Path): a temporary directory for artifacts.

    Returns:
        str: _description_
    """
    results = []
    with subprocess.Popen(["echo", source], stdout=subprocess.PIPE) as src_pipe:
        with subprocess.Popen(
            ["/usr/bin/gcc", "-c", "-o", tmp_dir / f"{module}.o", "-xc", "-"],
            stdin=src_pipe.stdout,
        ) as gcc_c_process:
            results.append(gcc_c_process.communicate())
    with subprocess.Popen(["/usr/bin/strip", tmp_dir / f"{module}.o"]) as strip_process:
        results.append(strip_process.communicate())
    return results


class Runner:
    """Wrapper around CCFI to run C code and compare results between different
     functions.

    Attributes:
    tmpdir (pathlib.Path): Storage of artifacts.
    compiled_modules (Set[str]): Already compiled modules, used to avoid name
    conflict.
    """

    def __init__(self, tmpdir: pathlib.Path):
        """Default init

        Args:
            tmpdir (pathlib.Path): Temporary directory for artifacts
        """
        self.tmpdir = tmpdir.resolve()
        self.compiled_modules = set()

    def compile(self, module: str, source: str, header: str) -> None:
        """Compile the source code using CFFI. Only tested for a single function
         in source.

        Args:
            module (str): module name (ie. output file name).
            source (str): source code
            header (str): function signatures that would be in a .h file.

        Raises:
            ValueError: if a compilation with same module name  has already been
             compiled
        """
        if module in self.compiled_modules:
            raise ValueError(f"Module ({module}) already compiled. Name conflict.")

        self.ffibuilder = FFI()
        self.ffibuilder.cdef(header)
        self.ffibuilder.set_source(module, source)
        self.ffibuilder.compile(verbose=False, tmpdir=str(self.tmpdir))
        self.compiled_modules.add(f"{module}")

    def run(self, module: str, funcname: str, *args: Any) -> Any:
        """Run an already compiled function. Modify path to include the
        artifacts directory.
        Import the compiled module with CFFI, and run the function.

        Args:
            module (str): module name
            funcname (str): function name

        Returns:
            Any: function run result
        """
        sys.path.insert(0, str(self.tmpdir))
        my_module = importlib.import_module(module)
        return self._run_function_by_name(my_module.lib, funcname, *args)

    def _run_function_by_name(self, module: str, funcname: str, *args) -> Any:
        """Find the function in a module, check its callable and run it using
        passed arguments.

        Args:
            module (str): module name
            funcname (str): function name

        Returns:
            Any: function run result
        """
        if hasattr(module, funcname) and callable(func := getattr(module, funcname)):
            return func(*args)

    def compile_and_run(self, module: str, function_source: str, *args) -> Any:
        """Helper that run compile and run function in one go

        Args:
            module (str): module name
            function_source (str): source code containing the function
            definition

        Returns:
            Any: function run result
        """
        function_definition = get_function_signatures(function_source)[0]
        function_name = get_function_name(function_definition)
        self.compile(module, function_source, function_definition)
        result = self.run(module, function_name, *args)
        return result

    def compare_functions(
        self, src_function_a: str, src_function_b: str, *args
    ) -> bool:
        """Compile and run two functions with the same arguments, and returns
        the comparison
        of the return value. The functions can be the same and have the same
        name.

        Args:
            src_function_a (str): function A source code
            src_function_b (str): function B source code

        Returns:
            bool: whether results are equals.
        """
        res_a = self.compile_and_run("module_a", src_function_a, *args)
        res_b = self.compile_and_run("module_b", src_function_b, *args)
        return res_a == res_b
