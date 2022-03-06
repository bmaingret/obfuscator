from obfuscator.examples import available_example_help, available_examples


def test_examples():
    examples = available_examples()
    assert "pi.c" in examples
    assert "sum42.c" in examples


def test_examples_help():
    help = available_example_help()
    assert "sum42.c: uint8_t f(uint32_t a, uint32_t b, uint32_t c);" in help
    assert "pi.c: float pi_approx(int n);" in help
