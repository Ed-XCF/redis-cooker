dev:
	- pip3 install -r requirements-dev.txt
test:
	- coverage run -m pytest -v
release:
	- pip3 install -r requirements.txt
build:
	- python3 setup.py sdist bdist_wheel
pypi:
	- twine upload dist/*
