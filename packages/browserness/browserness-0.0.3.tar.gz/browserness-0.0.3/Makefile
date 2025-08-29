# Makefile for building and publishing the browserness Python SDK

# Variables
PACKAGE_NAME = browserness
BUILD_DIR = dist
PYTHON = python

# Default target
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  build          - Build the package"
	@echo "  clean          - Clean build artifacts"
	@echo "  test-publish   - Publish to TestPyPI"
	@echo "  publish        - Publish to PyPI"
	@echo "  install        - Install the package in development mode"
	@echo "  check          - Check the package metadata"
	@echo "  help           - Show this help message"

# Clean build artifacts
.PHONY: clean
clean:
	@echo "Cleaning build artifacts..."
	rm -rf $(BUILD_DIR) build *.egg-info

# Build the package
.PHONY: build
build: clean
	@echo "Building the package..."
	$(PYTHON) -m build
	@echo "Build completed. Files in $(BUILD_DIR):"
	ls -la $(BUILD_DIR)

# Check the package metadata
.PHONY: check
check:
	@echo "Checking package metadata..."
	$(PYTHON) -m twine check $(BUILD_DIR)/*

# Install the package in development mode
.PHONY: install
install:
	@echo "Installing package in development mode..."
	$(PYTHON) -m pip install -e .

# Publish to TestPyPI
.PHONY: test-publish
test-publish: build check
	@echo "Publishing to TestPyPI..."
	@echo "Note: You may need to set TWINE_USERNAME and TWINE_PASSWORD environment variables"
	@echo "      or use --username and --password flags"
	$(PYTHON) -m twine upload --repository testpypi $(BUILD_DIR)/*

# Publish to PyPI
.PHONY: publish
publish: build check
	@echo "Publishing to PyPI..."
	@echo "Note: You may need to set TWINE_USERNAME and TWINE_PASSWORD environment variables"
	@echo "      or use --username and --password flags"
	$(PYTHON) -m twine upload $(BUILD_DIR)/*

# Run tests (if any)
.PHONY: test
test:
	@echo "Running tests..."
	# Add test commands here if you have tests
	# $(PYTHON) -m pytest

# Format code (if using a formatter)
.PHONY: format
format:
	@echo "Formatting code..."
	# Add formatting commands here if you use a code formatter
	# black .
	# isort .