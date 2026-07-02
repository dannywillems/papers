MAIN := main

.PHONY: help
help: ## Ask for help!
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; \
		{printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: build
build: ## Build the paper PDF with latexmk (pdflatex + biber)
	latexmk -pdf -interaction=nonstopmode -halt-on-error $(MAIN).tex

.PHONY: html
html: ## Build the paper as HTML (make4ht + MathJax)
	make4ht -u -f html5 $(MAIN).tex "mathjax"

.PHONY: watch
watch: ## Continuously rebuild on change
	latexmk -pdf -pvc -interaction=nonstopmode $(MAIN).tex

.PHONY: clean
clean: ## Remove LaTeX auxiliary files
	latexmk -c $(MAIN).tex

.PHONY: clean-all
clean-all: ## Remove auxiliary files, the PDF, and the HTML output
	latexmk -C $(MAIN).tex
	rm -f $(MAIN).html $(MAIN).css $(MAIN)*.svg \
		$(MAIN).4ct $(MAIN).4tc $(MAIN).idv $(MAIN).lg \
		$(MAIN).tmp $(MAIN).xref $(MAIN).dvi
