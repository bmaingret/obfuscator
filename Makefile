# https://github.com/aresponses/aresponses/blob/master/Makefile

.PHONY: clean require_pyenv init dev alint autoformat lint requirements

#################################################################################
# GLOBALS                                                                       #
#################################################################################

SHELL := /bin/bash
PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
PROJECT_NAME = obfuscator
PROJECT_SRC = obfuscator
PYTHON_VERSION = 3.9.4
VENV_NAME = zama_obfuscator
PYENV_INSTRUCTIONS=https://github.com/pyenv/pyenv#installation
PYENV_VIRT_INSTRUCTIONS=https://github.com/pyenv/pyenv-virtualenv#pyenv-virtualenv

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

## Setup a dev environment for local development.
init: require_pyenv  
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

## Install development dependencies
dev:
	python -m pip install -r requirements-dev.txt

## Shortcut for autoformat and lint - Requires to have run make dev
alint: autoformat lint

## Autoformat  using black and isort - Requires to have run make dev
autoformat:
	black $(PROJECT_SRC) notebooks
	isort --atomic $(PROJECT_SRC)

## Lint pylint and bandit - Requires to have run make dev
lint:
	python -m pylint $(PROJECT_SRC)
	bandit -r $(PROJECT_SRC)

## Delete all compiled Python files
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -delete

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
