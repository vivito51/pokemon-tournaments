FRONTEND_DIR=frontend
BACKEND_DIR=backend

.PHONY: frontend-install frontend-dev frontend-build backend-install backend-dev backend-scrape

frontend-install:
	cd $(FRONTEND_DIR) && npm install

frontend-dev:
	cd $(FRONTEND_DIR) && npm run dev

frontend-build:
	cd $(FRONTEND_DIR) && npm run build

backend-install:
	cd $(BACKEND_DIR) && python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt

backend-dev:
	cd $(BACKEND_DIR) && . venv/bin/activate && python run_api.py

backend-scrape:
	cd $(BACKEND_DIR) && . venv/bin/activate && python scrapper_runner.py
