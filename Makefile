dev:
	- pip3 install -r requirements-dev.txt
test:
	- coverage run -m pytest -v
release:
	- pip3 install -r requirements.txt
tag:
	- git tag -a v$(python3 setup.py --version)
