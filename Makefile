.PHONY: ship test

ship:
	python setup.py sdist bdist_wheel
	twine upload dist/* --skip-existing

test:
	flake8 bigbuild
	coverage run setup.py test
	coverage report -m
