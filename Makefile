.PHONY: help venv install run dev test lint docker-build docker-run docker-test

APP_MODULE=app.main:app
HOST=0.0.0.0
PORT=8000
IMAGE_NAME=discount-service:latest

help:
	@echo "make venv          - Create virtualenv"
	@echo "make install       - Install dependencies"
	@echo "make run           - Run API (uvicorn)"
	@echo "make dev           - Run API with reload"
	@echo "make test          - Run tests"
	@echo "make docker-build  - Build Docker image"
	@echo "make docker-run    - Run container"
	@echo "make docker-test   - Run tests inside container"

venv:
	python3 -m venv .venv
	. .venv/bin/activate; pip install --upgrade pip

install:
	. .venv/bin/activate; pip install -r requirements.txt

run:
	. .venv/bin/activate; uvicorn $(APP_MODULE) --host $(HOST) --port $(PORT)

dev:
	. .venv/bin/activate; uvicorn $(APP_MODULE) --host $(HOST) --port $(PORT) --reload

test:
	. .venv/bin/activate; pytest -q

docker-build:
	docker build -t $(IMAGE_NAME) .

docker-run:
	docker run --rm -p $(PORT):8000 -e DISCOUNT_DB_URL=sqlite:///./discounts.db $(IMAGE_NAME)

docker-test:
	docker run --rm $(IMAGE_NAME) pytest -q
