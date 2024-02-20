POETRY := $(shell command -v poetry 2> /dev/null)

.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "Please use 'make <target>' where <target> is one of"
	@echo ""
	@echo "  install     install packages and prepare environment"
	@echo ""
	@echo "Check the Makefile to know exactly what each target is doing."

install:
	@if [ -z $(POETRY) ]; then echo "Poetry could not be found. See https://python-poetry.org/docs/"; exit 2; fi
	$(POETRY) install

run:
	$(POETRY) run python src/simple_backup/app.py

build_exe:
	$(POETRY) run pyinstaller --onefile --clean --name whisper_watcher watcher.py --windowed

build_github_actions:
	pip install pyinstaller==6.2.0 loguru==0.7.2
	pyinstaller --onefile --clean --name SimpleBackup src/simple_backup/app.py --windowed