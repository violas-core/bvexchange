# Copyright (c) The Diem Core Contributors
# SPDX-License-Identifier: Apache-2.0

init:
	python3 -m venv ./venv

	./venv/bin/pip install --upgrade pip wheel setuptools
	./venv/bin/pip install -r requirements.txt

black:
	./venv/bin/python -m black --check src tests

lint:
	./venv/bin/pylama src tests examples
	./venv/bin/pyre --search-path venv/lib/python3.9/site-packages check

format:
	./venv/bin/python -m black src tests examples

test: format lint runtest

runtest:
	./venv/bin/pytest tests/test_* examples/* -s -k "$(t)" $(args)

cover:
	./venv/bin/pytest --cov-report html --cov=src tests/test_* examples/*

build: black lint runtest

dist:
	rm -rf build dist
	./venv/bin/python setup.py -q sdist bdist_wheel


publish: dist
	./venv/bin/pip install --upgrade twine
	./venv/bin/python3 -m twine upload dist/*

docs: init
	rm -rf docs/bridge
	rm -rf docs/examples

docker:
	docker-compose -f docker/testnet/docker-compose.yaml up --detach

docker-down:
	docker-compose -f docker/testnet/docker-compose.yaml down -v

docker-stop:
	docker-compose -f docker/testnet/docker-compose.yaml stop

.PHONY: init lint format test cover build diemtypes protobuf gen dist docs server docker docker-down docker-stop
