.DEFAULT_GOAL := help

.PHONY: docs test type-check fmt ci

test: ## Run tests
	pytest

type-check: ## Check all python types
	mypy panoramax_cli/

fmt: ## Format code
	ruff format

ci: type-check fmt test ## Run all check like the ci

docs:  ## Generates documentation from Typer embedded docs
	XDG_CONFIG_HOME='/home/a_user/.config' python -m typer ./panoramax_cli/main.py utils docs --name panoramax_cli --output docs/COMMANDS.md

help: ## Print this help message
	@grep -E '^[a-zA-Z_-]+:.*## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
