.PHONY: ship test updatetemplates

ship:
	python setup.py sdist bdist_wheel upload

test:
	flake8 bigbuild
	coverage run setup.py test
	coverage report -m

updatetemplates:
	cd `pwd`/bigbuild/templates/ && curl -O http://cookbook.latimes.com/templates/latest.zip && unzip -o latest.zip && rm latest.zip && cd `pwd`
