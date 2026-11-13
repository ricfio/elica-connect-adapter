.PHONY: help venv clean lint test install bump-version

VENV_PATH = .venv
PYTHON = python3

help:
	@echo "Usage: make [target]"
	@echo
	@echo "Available targets:"
	@awk 'BEGIN{FS=":"} \
	/^#/{comment=$$0; next} \
	/^[a-zA-Z_-]+:/{ \
		if (comment != "") { \
			gsub(/^# /,"",comment); \
			printf "  %-12s %s\n", $$1, comment; \
			comment="" \
		} \
	}' $(MAKEFILE_LIST)

# 🔨 Setup Python virtual environment
venv:
	$(PYTHON) -m venv $(VENV_PATH)
	@echo "✅ Virtual environment created."

# 🧹 Remove build artifacts, caches, and virtual environment
clean:
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@rm -rf $(VENV_PATH) .coverage .pytest_cache htmlcov
	@echo "✅ Clean complete."

# 🔍 Run code quality checks
lint:
	$(VENV_PATH)/bin/ruff check .
	$(VENV_PATH)/bin/ruff format --check .
	$(VENV_PATH)/bin/mypy custom_components

# ✨ Format code automatically with Ruff
format:
	$(VENV_PATH)/bin/ruff check --fix .
	$(VENV_PATH)/bin/ruff format .

# 🧪 Run tests with coverage
test:
	$(VENV_PATH)/bin/pytest --cov=custom_components/elica_connect_adapter tests/ -v
	@echo "✅ Tests complete."

# 📦 Install package in development mode
install:
	$(VENV_PATH)/bin/pip install -r requirements_test.txt
	@echo "✅ Dependencies installed."

# 🚀 Update release metadata (usage: make bump-version VERSION=0.2.4)
bump-version:
	@test -n "$(VERSION)" || (echo "Usage: make bump-version VERSION=X.Y.Z"; exit 2)
	$(PYTHON) scripts/bump-version.py $(VERSION)

# 🎯 Initialize development environment
init: clean venv install
	@echo "✅ Development environment initialized."
