# WERKAtlas: safe local verification by default. Never rewrite canonical files.
# Windows (without make): py scripts/local_workflow.py verify

.PHONY: all verify validate audit backlog test check-links collect enrich classify score render clean setup
.DEFAULT_GOAL := verify

all: verify

verify:
	python scripts/local_workflow.py verify

validate:
	python scripts/validate.py --catalog data/catalog.json --schema data/catalog.schema.json

audit:
	python scripts/local_workflow.py verify --skip-tests

backlog:
	python scripts/local_workflow.py backlog --limit 20

test:
	python -m pytest tests/ -q

# Explicit network check, not part of the default local workflow.
check-links:
	python scripts/check_links.py --catalog data/catalog.json

# Historical operations can overwrite catalog files or long-form documentation.
# Run them manually only after explicit backup and review.
collect enrich classify score render clean setup:
	@echo "Disabled from Makefile for safety. See docs/LOCAL-WORKFLOWS.md."
	@exit 2
