.DEFAULT_GOAL := all
isort = isort --float-to-top qcelemental
black = black qcelemental
autoflake = autoflake -ir --remove-all-unused-imports --ignore-init-module-imports --remove-unused-variables qcelemental

.PHONY: install
install:
	pip install -e .

.PHONY: format
format:
#	$(autoflake)
	$(isort)
	$(black)

.PHONY: lint
lint:
	$(isort) --check-only
	$(black) --check

.PHONY: check-dist
check-dist:
	python setup.py check -ms
	python setup.py sdist
	twine check dist/*

.PHONY: mypy
mypy:
	mypy qcelemental

.PHONY: test
test:
	pytest -v --cov=qcelemental/

.PHONY: data
data: cpu_data
	#(cd devtools/scripts; python build_periodic_table.py; mv nist_*_atomic_weights.py ../../qcelemental/data/)
	#(cd devtools/scripts; python build_physical_constants_2014.py; mv nist_*_codata.py ../../qcelemental/data/)
	(cd raw_data/dft_data; python build_dft_info.py; mv dft_data_blob.py ../../qcelemental/info/data/)
	(cd devtools/scripts; python build_physical_constants_2018.py; mv nist_*_codata.py ../../qcelemental/data/)

.PHONY: cpu_data
cpu_data:
	(cd raw_data/cpu_data; python build_cpu_data.py; mv cpu_data_blob.py ../../qcelemental/info/data/)

.PHONY: clean
clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
	rm -rf .cache
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf *.egg-info
	rm -f .coverage
	rm -f .coverage.*
	rm -rf build
	rm -rf dist
	rm -f qcelemental/*.c qcelemental/*.so
	python setup.py clean
