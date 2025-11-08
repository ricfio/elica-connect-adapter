.PHONY: help venv clean lint test install

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
	$(VENV_PATH)/bin/black .
	$(VENV_PATH)/bin/isort .
	$(VENV_PATH)/bin/pylint custom_components tests
	@echo "✅ Code quality checks complete."

# 🧪 Run tests with coverage
test:
	$(VENV_PATH)/bin/pytest --cov=custom_components/elica_connect tests/ -v
	@echo "✅ Tests complete."

# 📦 Install package in development mode
install:
	$(VENV_PATH)/bin/pip install -r requirements_test.txt
	@echo "✅ Dependencies installed."

# 🎯 Initialize development environment
init: clean venv install
	@echo "✅ Development environment initialized."
