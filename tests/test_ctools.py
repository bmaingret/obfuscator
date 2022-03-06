import pathlib

from obfuscator import ctools

BASIC_FUNCTION = r"""uint8_t f(uint32_t a, uint32_t b, uint32_t c)
{
    uint8_t res;
    res = a + b + c + 42;
    return res;
}"""

BASIC_SIGNATURE = "uint8_t f(uint32_t a, uint32_t b, uint32_t c);"

INCLUDES_LIST = r'''# include <stdlib.h>
#include <math.h>

# include "stdint.h"'''


def test_gcc_compile(c_file: pathlib.Path, tmp_path: pathlib.Path):
    tmp_path.mkdir(exist_ok=True)
    source_code = c_file.open().read()
    ctools.gcc_compile(module="test", source=source_code, tmp_dir=tmp_path)
    assert (tmp_path / "test.o").exists()


def test_include_lib():
    assert ctools.generate_include_lib_str("stdin.h") == "#include <stdin.h>"


def test_is_lib_included():
    assert True == ctools.is_lib_included(INCLUDES_LIST, "stdlib.h")
    assert True == ctools.is_lib_included(INCLUDES_LIST, "math.h")
    assert True == ctools.is_lib_included(INCLUDES_LIST, "stdint.h")
    assert False == ctools.is_lib_included(INCLUDES_LIST, "stdio.h")


def test_function_def():
    ctools.get_function_signatures(BASIC_FUNCTION)
    assert BASIC_SIGNATURE == ctools.get_function_signatures(BASIC_FUNCTION)[0]


def test_insert_lib():
    source = ""
    lib = "testlib.h"
    source_and_lib = ctools.insert_lib(source, lib)
    assert source_and_lib == ctools.generate_include_lib_str(lib) + "\n"
    source_and_lib = ctools.insert_lib(source_and_lib, lib)
    assert source_and_lib == ctools.generate_include_lib_str(lib) + "\n"


def test_get_function_name():
    ctools.get_function_name(BASIC_SIGNATURE)
    assert "f" == ctools.get_function_name(BASIC_SIGNATURE)
    try:
        ctools.get_function_name("")
    except ValueError:
        assert True
        return
    assert False


def test_count_args():
    assert 3 == ctools.count_args("uint8_t f(uint32_t a, uint32_t b, uint32_t c);")


def test_comile_raises(tmp_path: pathlib.Path):
    runner = ctools.Runner(tmp_path)
    runner.compile("test", BASIC_FUNCTION, BASIC_SIGNATURE)
    try:
        runner.compile("test", BASIC_FUNCTION, BASIC_SIGNATURE)
    except ValueError:
        assert True
        return
    assert False
