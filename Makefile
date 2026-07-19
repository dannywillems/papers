# List of paper directories, built one after another. Keep this list in
# sync with the build steps in .github/workflows/build.yaml.
PAPERS := \
	2026-07-02-authenticated-data-structures

.PHONY: help
help: ## Ask for help!
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; \
		{printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: build
build: ## Build every paper, one after another
	@for p in $(PAPERS); do \
		echo "==> building $$p"; \
		$(MAKE) -C "$$p" build || exit 1; \
	done

.PHONY: html
html: ## Build every paper as HTML, one after another
	@for p in $(PAPERS); do \
		echo "==> html $$p"; \
		$(MAKE) -C "$$p" html || exit 1; \
	done

.PHONY: site-assets
site-assets: ## Compile the site's TypeScript assets (requires Node)
	cd tools/site_assets && npm ci && npx tsc -p .

.PHONY: assemble-site
assemble-site: ## Assemble site/ from built HTML and compiled assets
	python3 tools/build_site.py $(PAPERS)

.PHONY: site
site: site-assets html assemble-site ## Build the GitHub Pages site

.PHONY: clean
clean: ## Clean auxiliary files in every paper
	@for p in $(PAPERS); do \
		echo "==> cleaning $$p"; \
		$(MAKE) -C "$$p" clean-all || exit 1; \
	done
	rm -rf site

.PHONY: lint-shell
lint-shell: ## Lint shell scripts using shellcheck
	@files=$$(find . -type f -name '*.sh' \
		-not -path '*/.lake/*' -not -path '*/.venv/*' \
		-not -path '*/node_modules/*'); \
	if [ -z "$$files" ]; then \
		echo "No shell scripts to lint"; \
	else \
		echo "$$files" | xargs shellcheck; \
	fi
