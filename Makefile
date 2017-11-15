.PHONY: core-requirements update-pip-requirements requirements clean-pyc \
	fix-virtualenv-python develop reports pycodestyle flake8 check8 test

core-requirements:
	pip install "pip>=9,<9.1" setuptools "pip-tools>=1"

update-pip-requirements: core-requirements
	pip install -U "pip>=9,<9.1" setuptools "pip-tools>=1"
	pip-compile -U requirements/base.in
	pip-compile -U requirements/dev.in

requirements: core-requirements
	pip-sync requirements/base.txt requirements/dev.txt

clean-pyc: requirements
	find . -iname "*.pyc" -delete

fix-virtualenv-python: requirements
	fix-osx-virtualenv $VIRTUAL_ENV
	# Only works for Python 3.5 on OSX!
	test -h $VIRTUAL_ENV/bin/python3.5 || (cd $VIRTUAL_ENV/bin && mv python3.5 original-python3.5 && ln -s python python3.5)

develop: clean-pyc fix-virtualenv-python
	python setup.py develop

reports:
	mkdir -p $@

pycodestyle: reports requirements
	set -o pipefail && $@ bdwx | tee reports/$@.report

flake8: reports requirements
	set -o pipefail && $@ bdwx | tee reports/$@.report

check8: pycodestyle flake8

test: check8
