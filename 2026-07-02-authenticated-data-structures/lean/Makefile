.PHONY: help
help: ## Ask for help!
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; \
		{printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: build
build: ## Build the library and demo, rejecting any sorry
	lake build --wfail

.PHONY: run
run: ## Run the demonstration executable
	lake exe adsdemo

.PHONY: check-sorry
check-sorry: ## Fail if any sorry or admit remains in the sources
	@! grep -rn "sorry\|admit" Ads Ads.lean Main.lean

.PHONY: check
check: check-sorry build run ## Build (no sorry), then run the demo

.PHONY: clean
clean: ## Remove Lake build outputs
	lake clean
