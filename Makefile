
docker-image:
	docker build . --file Dockerfile --tag markusressel/telegram-click:latest

test:
	pytest


lock:
	./venv/bin/python -m pip install -U pipenv
	./venv/bin/pipenv lock
