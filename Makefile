.PHONY: updatetemplates

updatetemplates:
	cd `pwd`/bigbuild/templates/ && curl -O http://cookbook.latimes.com/templates/latest.zip && unzip -o latest.zip && rm latest.zip && cd `pwd`
