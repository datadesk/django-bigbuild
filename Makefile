.PHONY: ship test html livehtml build

ship:
	python setup.py sdist bdist_wheel
	twine upload dist/* --skip-existing

test:
	flake8 bigbuild
	coverage run setup.py test
	coverage report -m

docs:
	cd docs && make html

docslive:
	cd docs && make livehtml

build:
	clear
	rm -rf .build
	python example/manage.py build bigbuild.views.PageListView --skip-media --skip-static
	ls .build
