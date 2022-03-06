# https://github.com/aresponses/aresponses/blob/master/Makefile

.PHONY: clean require_pyenv init dev alint autoformat lint requirements

#################################################################################
# GLOBALS                                                                       #
#################################################################################

SHELL := /bin/bash
PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
PROJECT_NAME = obfuscator
PROJECT_SRC = obfuscator
TEST_DIR = tests
PYTHON_VERSION = 3.9.4
VENV_NAME = zama_obfuscator
PYENV_INSTRUCTIONS=https://github.com/pyenv/pyenv#installation
PYENV_VIRT_INSTRUCTIONS=https://github.com/pyenv/pyenv-virtualenv#pyenv-virtualenv
PYCPARSER_RELEASE=release_v2.20
#################################################################################
# COMMANDS                                                                      #
#################################################################################

## Check pyenv and pyenv-virtualenv installations
require_pyenv:
	@if ! [ -x "$$(command -v pyenv)" ]; then\
	  echo -e '\n\033[0;31m ❌ pyenv is not installed.  Follow instructions here: $(pyenv_instructions)\n\033[0m';\
	  exit 1;\
	else\
	  echo -e "\033[0;32m ✔️  pyenv installed\033[0m";\
	fi
	@if ! [[ "$$(pyenv virtualenv --version)" == *"pyenv-virtualenv"* ]]; then\
	  echo -e '\n\033[0;31m ❌ pyenv virtualenv is not installed.  Follow instructions here: $(pyenv_virt_instructions) \n\033[0m';\
	  exit 1;\
	else\
	  echo -e "\033[0;32m ✔️  pyenv-virtualenv installed\033[0m";\
	fi

require_tools:
	@if ! [ -x "$$(command -v curl)" ]; then\
	  echo -e '\n\033[0;31m ❌ curl is not installed.  Please install it.\n\033[0m';\
	  exit 1;\
	else\
	  echo -e "\033[0;32m ✔️  curl installed\033[0m";\
	fi
	@if ! [ -x "$$(command -v unzip)" ]; then\
	  echo -e '\n\033[0;31m ❌ unzip is not installed.  Please install it.\n\033[0m';\
	  exit 1;\
	else\
	  echo -e "\033[0;32m ✔️  unzip installed\033[0m";\
	fi		
	@if ! [ -x "$$(command -v sed)" ]; then\
	  echo -e '\n\033[0;31m ❌ sed is not installed.  Please install it.\n\033[0m';\
	  exit 1;\
	else\
	  echo -e "\033[0;32m ✔️  sed installed\033[0m";\
	fi		

require_poetry:
	@if ! [ -x "$$(command -v poetry)" ]; then\
	  echo -e '\n\033[0;31m ❌ poetry is not installed.  Please install it: https://python-poetry.org/docs/#installation.\n\033[0m';\
	  exit 1;\
	else\
	  echo -e "\033[0;32m ✔️  poetry installed\033[0m";\
	fi

## Setup a Python environment for local development.
init: require_pyenv require_tools
	@pyenv install $(PYTHON_VERSION) -s
	@echo -e "\033[0;32m ✔️  🐍 $(PYTHON_VERSION) installed \033[0m"
	@if ! [ -d "$$(pyenv root)/versions/$(VENV_NAME)" ]; then\
		pyenv virtualenv $(PYTHON_VERSION) $(VENV_NAME);\
	fi;
	@pyenv local $(VENV_NAME)
	@echo -e "\033[0;32m ✔️  🐍 $(VENV_NAME) virtualenv activated \033[0m"
	python -m pip install --upgrade pip
	@echo -e "\nEnvironment setup! ✨ 🍰 ✨ 🐍 \n\n"
	@echo -e "\033[0;32m"
	@pyenv which python
	@echo -e "\n\033[0m"
	@echo -e "You should probably run make requirements or make dev.\n"
	@make -s help	


## Install Python Dependencies
requirements: init
	python -m pip install -r requirements.txt
	curl -SL https://github.com/eliben/pycparser/archive/refs/tags/${PYCPARSER_RELEASE}.zip -o pycparser-${PYCPARSER_RELEASE}.zip
	unzip -o pycparser-${PYCPARSER_RELEASE}.zip
	cp -R pycparser-${PYCPARSER_RELEASE}/utils/fake_libc_include $(PROJECT_SRC)/data/
	rm pycparser-${PYCPARSER_RELEASE}.zip
	rm -rf pycparser-${PYCPARSER_RELEASE}

## Install development dependencies
dev: requirements
	python -m pip install -r requirements-dev.txt
	curl -SL https://github.com/google/styleguide/raw/gh-pages/pylintrc -o .pylintrc
	sed -i 's/indent-string='\''  '\''/indent-string='\''    '\''/g' .pylintrc
	sed -i 's/max-line-length=80/max-line-length=88/g' .pylintrc
	
## Shortcut for autoformat and lint - Requires to have run make dev
alint: autoformat lint

## Autoformat  using black and isort - Requires to have run make dev
autoformat:
	autoflake --in-place --remove-unused-variables --remove-all-unused-imports --expand-star-imports --recursive $(PROJECT_SRC) $(TEST_DIR)
	black $(PROJECT_SRC) $(TEST_DIR) conftest.py
	isort --atomic $(PROJECT_SRC) $(TEST_DIR)

## Lint pylint and bandit - Requires to have run make dev
lint:
	python -m pylint --rcfile=.pylintrc --exit-zero $(PROJECT_SRC)

## Delete all compiled Python files
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -delete
	find . -name '.pytest_cache' -type d | xargs rm -rf
	find . -name '.cffi_build' -type d | xargs rm -rf
	find . -name '.coverage' -delete
	find . -name 'lextab.py' -delete
	find . -name 'yacctab.py' -delete


## Run tests - Requires to have run make dev
test:
	pytest --verbose

## Run test coverage - Requires to have run make dev
cov:
	coverage run
	coverage report

## Generate typer application documentation - Requires to have run make dev
cli_docs: 
	typer obfuscator/cli.py utils docs --name bmaingret-obfuscator --output CLI_DOCS.md   

## Build Python wheel and sdist using Poetry
build: alint test require_poetry
	find . -name '*.whl' -delete
	find . -name '*.tar.gz' -delete	
	poetry update
	poetry build
	poetry export -f requirements.txt --output requirements.txt --without-hashes
	poetry export --dev -f requirements.txt --output requirements-dev.txt --without-hashes

# Build pdf from REPORT.md using Pandoc
report:
	@if ! [ -x "$$(command -v pandoc)" ]; then\
	  echo -e '\n\033[0;31m ❌ pandoc is not installed.  Please install it. (apt install texlive texlive-latex-extra pandoc ?)\n\033[0m';\
	  exit 1;\
	else\
	  echo -e "\033[0;32m ✔️  pandoc installed\033[0m";\
	fi		
	pandoc REPORT.md -s -o zama_bmaingret_obfuscator_report.pdf

## Zip the content of the repository
zip: build clean cli_docs report
	cd .. && zip -FSr bmaingret_obfuscator.zip obfuscator  -x */\bmaingret_obfuscator.zip -x .vscode/\* -x .git/\*       

#################################################################################
# PROJECT RULES                                                                 #
#################################################################################

#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

# Inspired by <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
# sed script explained:
# /^##/:
# 	* save line in hold space
# 	* purge line
# 	* Loop:
# 		* append newline + line to hold space
# 		* go to next line
# 		* if line starts with doc comment, strip comment character off and loop
# 	* remove target prerequisites
# 	* append hold space (+ newline) to line
# 	* replace newline plus comments by `---`
# 	* print line
# Separate expressions are necessary because labels cannot be delimited by
# semicolon; see <http://stackoverflow.com/a/11799865/1968>
.PHONY: help
help:
	@echo "$$(tput bold)Available rules:$$(tput sgr0)"
	@echo
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')
