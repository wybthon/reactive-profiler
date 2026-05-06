# Reactive Profiler: local development helpers.
#
# Targets:
#   make           Show this help
#   make manifest  Regenerate app/manifest.json from app/**/*.py
#   make check     Verify app/manifest.json is up to date (CI-friendly)
#   make serve     Serve the static site at http://localhost:8000
#   make dev       Regenerate the manifest, then serve

PORT ?= 8000

.PHONY: help manifest check serve dev clean

help:
	@echo "Reactive Profiler: make targets"
	@echo "  make manifest   Regenerate app/manifest.json"
	@echo "  make check      Fail if app/manifest.json is stale"
	@echo "  make serve      python -m http.server $(PORT)"
	@echo "  make dev        manifest + serve"
	@echo "  make clean      Remove __pycache__ trees"

manifest:
	python3 tools/build_manifest.py

check:
	python3 tools/build_manifest.py --check

serve:
	@echo "Serving on http://localhost:$(PORT)"
	python3 -m http.server $(PORT)

dev: manifest serve

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
