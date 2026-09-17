.PHONY: help install test seed run-backend run-frontend build

help:
	@echo "SupportSwarm Development Commands:"
	@echo "  make install       - Set up backend venv and install frontend npm packages"
	@echo "  make test          - Run full backend test suite with pytest"
	@echo "  make seed          - Seed persistent database with 50+ customers & 100+ tickets"
	@echo "  make run-backend   - Start FastAPI server on port 8000"
	@echo "  make run-frontend  - Start Next.js frontend on port 3000"
	@echo "  make build         - Run production Next.js build"

install:
	python3 -m venv backend/venv
	backend/venv/bin/pip install -r backend/requirements.txt
	cd frontend && npm install

test:
	backend/venv/bin/pytest backend/tests/ -v

seed:
	backend/venv/bin/python3 backend/app/seed/run_seed.py

run-backend:
	backend/venv/bin/uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload

run-frontend:
	cd frontend && npm run dev

build:
	cd frontend && npm run build
