.PHONY: setup format lint test integration docs clean

REQUIRED_ENV_VARS = SCH_TOKEN SCH_CREDENTIAL_ID SDC_VERSION TRANSFORMER_VERSION ASTER_URL

all:
	@echo "\033[1;32mTo run a specific target, use: make <target>\033[0m"
	@echo "\033[1;32mAvailable targets:\033[0m"
	@grep -E '^[a-zA-Z0-9_-]+:' Makefile | grep -Ev '^all:|^validate:' | sed -E 's/([^:]+):.*/- \1/g' | sort

setup:
	@pip3 install -r build_requirements.txt
	@pip install -r test_requirements.txt

validate:
	@$(foreach env_var,$(REQUIRED_ENV_VARS), \
		$(if $(value $(env_var)),, \
			$(error Environment variable $(env_var) is not defined)))

format:
	black --config=evergreen/pyproject.toml streamsets/sdk tests
	isort --settings-path=evergreen/pyproject.toml streamsets/sdk tests

lint:
	flake8 --config=evergreen/.flake8 streamsets/sdk

test:
ifeq ($(filter test,$(MAKECMDGOALS)),)
	@pytest -v --disable-warnings --cov=streamsets/sdk tests/unit
else
	@pytest -v --disable-warnings --cov=streamsets/sdk -k "$(word 2,$(MAKECMDGOALS))" tests/unit
endif


integration: validate
ifeq ($(filter integration,$(MAKECMDGOALS)),)
	@pytest -v \
        --cov=streamsets/sdk \
        --disable-warnings \
        --sch-credential-id=$$SCH_CREDENTIAL_ID \
        --sch-token=$$SCH_TOKEN \
        --sdc-version=$$SDC_VERSION \
        --transformer-version=$$TRANSFORMER_VERSION \
        --aster-url=$$ASTER_URL \
        tests/integration
else
	@pytest -v \
		--cov=streamsets/sdk \
		--disable-warnings \
		--sch-credential-id=$$SCH_CREDENTIAL_ID \
		--sch-token=$$SCH_TOKEN \
		--sdc-version=$$SDC_VERSION \
		--transformer-version=$$TRANSFORMER_VERSION \
		--aster-url=$$ASTER_URL \
		-k "$(word 2,$(MAKECMDGOALS))" \
		tests/integration
endif

docs:
	@pip install -r docs/requirements.txt
	sphinx-build -b html -d .sphinx-build docs html

build:
	@python3 -m build

clean:
	@rm -rf venv html build dist htmlcov .sphinx-build .coverage .eggs *.egg-info
	@find . -type f -name '*.pyc' -delete
	@find . -type f -name '*.pyo' -delete
	@find . -type f -name '*_unit_*.xml' -delete
	@find . -type f -name '*_integration_*.xml' -delete
	@find . -type f -name 'coverage.xml' -delete
	@find . -type d -name '__pycache__' -prune -exec rm -rf "{}" \;
	@find . -type d -name '.pytest_cache' -prune -exec rm -rf "{}" \;
	@find . -type f -name '*~' -delete
