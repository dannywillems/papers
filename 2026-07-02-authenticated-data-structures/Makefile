MAIN := main

.PHONY: help
help: ## Ask for help!
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; \
		{printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: build
build: ## Build the paper PDF with latexmk (pdflatex + biber)
	latexmk -pdf -interaction=nonstopmode -halt-on-error $(MAIN).tex

.PHONY: watch
watch: ## Continuously rebuild on change
	latexmk -pdf -pvc -interaction=nonstopmode $(MAIN).tex

.PHONY: clean
clean: ## Remove LaTeX auxiliary files
	latexmk -c $(MAIN).tex

.PHONY: clean-all
clean-all: ## Remove auxiliary files and the built PDF
	latexmk -C $(MAIN).tex
