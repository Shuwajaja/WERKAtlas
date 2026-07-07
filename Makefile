.PHONY: all setup collect enrich classify score render validate check-links test clean

# Default target
all: validate render

# Setup: install dependencies
setup:
	uv pip install -r scripts/requirements.txt 2>/dev/null || true

# LOOP 1: Collect candidates from GitHub API and curated lists
collect:
	python scripts/collect.py --candidates-file data/candidates.ndjson --sources-file data/sources.json

# LOOP 2: Enrich candidate metadata via GitHub API
enrich:
	python scripts/enrich.py --candidates data/candidates.ndjson --catalog data/catalog.json

# LOOP 3: Classify candidates into categories
classify:
	python scripts/classify.py --input data/catalog.json --taxonomy data/taxonomy.json --output data/catalog.json

# LOOP 4: Score and rank projects
score:
	python scripts/score.py --input data/catalog.json --output data/catalog.json

# LOOP 5: Render all Markdown files
render:
	python scripts/render.py --catalog data/catalog.json --taxonomy data/taxonomy.json --output .

# Validate catalog
validate:
	python scripts/validate.py --catalog data/catalog.json --schema data/catalog.schema.json

# Check external links
check-links:
	python scripts/check_links.py --catalog data/catalog.json

# Run all tests
test:
	python -m pytest tests/ -v

# Clean generated files (keep data)
clean:
	rm -f research/LOOP-*.md
	rm -f research/subagents/*
	rm -f data/candidates.ndjson data/catalog.json data/catalog.csv data/rejected.json
