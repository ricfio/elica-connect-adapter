.PHONY: help clean

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

# 🧹 Remove build artifacts, caches, and virtual environment
clean:
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@echo "✅ Clean complete."
