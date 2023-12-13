ALL: install-libs

requirements.txt: requirements.in
	pip-compile

install-libs: requirements.txt
	pip install -r requirements.txt

.PHONY: install-libs
