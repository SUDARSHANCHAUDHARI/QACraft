PYTHON ?= python3

.PHONY: generate validate test serve package

generate:
	$(PYTHON) scripts/generate_docs.py

validate:
	$(PYTHON) scripts/validate_repo.py

test:
	$(PYTHON) -m unittest discover -s tests -v

serve:
	$(PYTHON) scripts/serve.py

package: validate test
	@echo "Repository is ready to package."
