# obfuscator: obfuscating C source code with Python - Proof of concept

## Requirements

In addition to Python toolings:

* gcc

And to fully use the makefile:

* pyenv
* curl
* zip/unzip
* sed
* poetry
* and obvisouly make

Tested with `Python 3.9.4`. We recommend using `pyenv` to install an adequate Python version.


## Install

Either install the wheel from the `dist` folder:

```console
$ python -m pip install bmaingret_obfuscator-0.1.0-py3-none-any.whl
```

Or install locally:

```console
$ python -m pip install .
```

Or run it from source and simply install dependencies:

```
$ python -m pip install -r requirements.txt
```

## Usage

If the package was installed, the `bmaingret-obfuscator` should be available (you might have to reload your shell):

```
$ exec $SHELL
$ bmaingret-obfuscator --help
$ bmaingret-obfuscator obfuscate --help
```

Else run it as a standard python module (Note the difference in name. Here we locate the module name, whereas previously we used the package name to prevent name clashes if installed on a system.):

```
$ python -m obfuscator --help
$ python -m obfuscator demo --help
```

They are two main commands:

* `obfuscate`: obfuscate source file located at the path passed as an argument
* `demo`: run obfuscator on example source files

Full documentation (in addition to running the command with `--help`) can be found in [CLI_DOCS.md](CLI_DOCS.md). Note that if running from source, you'll have to replace `bmaingret-obfuscator` by `obfuscator`.

## Tests

Tests are written with `pytest` and can be run against the source code:

```
$ python -m pip install requirements-dev.txt
$ make test
$ make cov
coverage report
Name                       Stmts   Miss  Cover   Missing
--------------------------------------------------------
obfuscator/__init__.py        18      0   100%
obfuscator/__main__.py         0      0   100%
obfuscator/cli.py             62      0   100%
obfuscator/cparser.py         18      0   100%
obfuscator/ctools.py          73      0   100%
obfuscator/examples.py        10      0   100%
obfuscator/techniques.py      44      0   100%
--------------------------------------------------------
TOTAL                        225      0   100%
```

## Makefile

Important note: the makefile is more used as a shortcut for multiple commands than its original intent. As such, and to prevent having  `pip install -r requirements-dev.txt` run each time we run tests, some dependencies are not reflected in the makefile. They should however be reflected in its documentation.

```
$ make
Available rules:

alint               Shortcut for autoformat and lint - Requires to have run make dev 
autoformat          Autoformat using black and isort - Requires to have run make dev 
build               Build Python wheel and sdist using Poetry 
clean               Delete all compiled Python files 
cli_docs            Generate typer application documentation - Requires to have run make dev 
cov                 Run test coverage - Requires to have run make dev 
dev                 Install development dependencies 
init                Setup a Python environment for local development. 
lint                Lint pylint and bandit - Requires to have run make dev 
requirements        Install Python Dependencies 
require_pyenv       Check pyenv and pyenv-virtualenv installations 
test                Run tests - Requires to have run make dev 
zip                 Zip the content of the repository 
```

## Lint and autoformat

Configurations can be found in `pyproject.toml`. Using [Google](https://github.com/google/styleguide/blob/gh-pages/pylintrc) `.pylintrc` with some tweaks (c.f. makefile `dev`).

* autoflake
* black
* isort
* bandit

```
$ make lint
[---]
-----------------------------------
Your code has been rated at 9.67/10
```
