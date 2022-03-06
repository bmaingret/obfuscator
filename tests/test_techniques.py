import pathlib

from obfuscator.techniques import (
    PassthroughTechnique,
    RemoveSpacesTechnique,
    ReplaceAdditionTechnique,
    ReplaceSingleAdditionTechnique,
    ReplaceXORTechnique,
    ReplacingTechnique,
)


def test_passthrough_technique_doesnt_change_code(c_file: pathlib.Path):
    with open(c_file, "r") as source_code:
        assert source_code == PassthroughTechnique.apply(source_code)


def test_remove_new_line_technique():
    test = r"""A;
B   C{
D}
"""
    expected = "A;B   C{D}"
    assert RemoveSpacesTechnique.apply(test) == expected


def test_replace_addition_technique():
    test = "res = a + b + c + 42;"
    expected = "res = (-(-a + (-b))) + (-(-c + (-42)));"
    assert ReplaceAdditionTechnique.apply(test) == expected


def test_replace_single_addition_technique():
    test = "res = a + b;"
    expected = (
        "#include <stdlib.h>\nr = rand (); res = a + r; res = res + b; res = res - r;"
    )
    assert ReplaceSingleAdditionTechnique.apply(test) == expected


def test_replace_xor_technique():
    test = r"res = a ^ b;"
    expected = r"res = (~a & b) | (a & ~b);"
    assert ReplaceXORTechnique.apply(test) == expected


def test_not_implemented_replacement_property():
    assert NotImplementedError == ReplacingTechnique.PATTERN
    assert NotImplementedError == ReplacingTechnique.REPLACEMENT
