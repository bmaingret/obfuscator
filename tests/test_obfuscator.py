import filecmp
import pathlib

from obfuscator import (
    HarderToRead,
    PassthroughObfuscator,
    ReplacementObfuscator,
    ctools,
)


def test_passthroughobfuscator_doesnt_change_code(c_file: pathlib.Path):
    obfuscator = PassthroughObfuscator()
    with open(c_file, "r") as source_code:
        assert source_code == obfuscator.obfuscate(source_code)


def test_hardertoread_obfuscator(c_file: pathlib.Path, tmp_path: pathlib.Path):
    obfuscator = HarderToRead()
    tmp_path.mkdir(exist_ok=True)

    source_code = c_file.read_text()
    obfuscated = obfuscator.obfuscate(source_code)
    path = tmp_path / c_file.name
    path.write_text(source_code)
    (tmp_path / f"{c_file.stem}_obfuscated{c_file.suffix}").open(mode="w").write(
        obfuscated
    )

    ctools.gcc_compile(module="original", source=source_code, tmp_dir=tmp_path)
    ctools.gcc_compile(module="obfuscated", source=obfuscated, tmp_dir=tmp_path)

    assert filecmp.cmp(tmp_path / "original.o", tmp_path / "obfuscated.o")


def test_replacementobfuscator_doesnt_change_result(
    c_file: pathlib.Path, tmp_path: pathlib.Path
):
    source_code = c_file.read_text()
    obfuscated = ReplacementObfuscator().obfuscate(source_code)

    header = ctools.get_function_signatures(source_code)[0]
    n_args = ctools.count_args(header)
    args = [i for i in range(1, 1 + n_args)]

    runner = ctools.Runner(pathlib.Path(tmp_path))
    runner.compare_functions(source_code, obfuscated, *args)


def test_replacementobfuscator_change_bytecode(
    c_file: pathlib.Path, tmp_path: pathlib.Path
):
    obfuscator = ReplacementObfuscator()
    tmp_path.mkdir(exist_ok=True)

    source_code = c_file.read_text()
    obfuscated = obfuscator.obfuscate(source_code)
    path = tmp_path / c_file.name
    path.write_text(source_code)
    (tmp_path / f"{c_file.stem}_obfuscated{c_file.suffix}").open(mode="w").write(
        obfuscated
    )

    ctools.gcc_compile(module="original", source=source_code, tmp_dir=tmp_path)
    ctools.gcc_compile(module="obfuscated", source=obfuscated, tmp_dir=tmp_path)

    assert False == filecmp.cmp(tmp_path / "original.o", tmp_path / "obfuscated.o")
