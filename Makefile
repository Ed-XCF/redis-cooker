dev:
	- pip3 install -r requirements-dev.txt
test:
	- coverage run -m pytest -v
