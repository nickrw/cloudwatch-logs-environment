SHELL := /bin/bash

default: test dist

dist: venv-python3
	venv-python3/bin/python setup.py bdist_wheel --universal

venv-%: requirements.txt requirements-dev.txt
	virtualenv -p $* $@
	$@/bin/pip install -r <(cat requirements.txt requirements-dev.txt)
	touch $@

lint-%: venv-%
	venv-$*/bin/flake8 cloudwatch_logs_environment

#test-%: venv-%
#	venv-$*/bin/py.test cloudwatch_logs_environment

# test: lint-python3 test-python3
test:
	@echo "Skipping tests, they haven't been written yet"

clean:
	rm -rf build dist *.egg-info

clean-all: clean
	rm -rf venv-python2 venv-python3

doc:
	pandoc --from=markdown --to=rst --output=README.rst README.md

pypi: venv-python3
	venv-python3/bin/python setup.py bdist_wheel --universal sdist upload

tag: venv-python3
	git tag $(shell venv-python3/bin/python setup.py --version)

.PHONY: lint-% test-% test clean clean-all
