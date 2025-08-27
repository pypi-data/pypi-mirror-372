
.PHONY: setup setup11 pydeps test bench-ci bench test-integration test-all coverage-report
.PHONY: test-resetup lint fix docs kind kind-teardown kuberay kuberay11 notebook

setup: kind-teardown kuberay pydeps

setup11: kind-teardown kuberay11 pydeps

pydeps:
	uv sync --all-groups --all-extras --no-extra prefect --locked

# Ray 2.47+ is known to have some issues with uv.  ray workers would start up
# with no ray library available and hang unit tests.  A workaround is set
# RAY_ENABLE_UV_RUN_RUNTIME_ENV=0.   See this for details:
# https://github.com/ray-project/ray/issues/53848#issuecomment-3056271943

test:
	RAY_ENABLE_UV_RUN_RUNTIME_ENV=0 uv run -m pytest src/tests --cov=src/geneva --cov-report=term-missing

test-flaky:
	# only run flaky tests (currently multibackfill tests)
	RAY_ENABLE_UV_RUN_RUNTIME_ENV=0 uv run -m pytest src/tests --cov=src/geneva -m multibackfill --cov-report=term-missing

test-no-flaky:
	RAY_ENABLE_UV_RUN_RUNTIME_ENV=0 uv run -m pytest src/tests --cov=src/geneva -m "not multibackfill" --cov-report=term-missing

bench-ci:
	RAY_ENABLE_UV_RUN_RUNTIME_ENV=0 uv run -m pytest src/benches -rx --cov=src/geneva --cov-append -v --benchmark-disable

bench:
	RAY_ENABLE_UV_RUN_RUNTIME_ENV=0 uv run -m pytest src/benches -v --benchmark-compare --benchmark-autosave --benchmark-save-data --benchmark-group-by=name --benchmark-verbose -s

test-integration-gcp:
	uv run -m pytest src/integ_tests --csp=gcp --test-slug=$(SLUG) --cov=src/geneva --cov-append -v -s --cov-report=term-missing

test-integration-aws:
	uv run -m pytest src/integ_tests --csp=aws --test-slug=$(SLUG) --cov=src/geneva --cov-append -v -s --cov-report=term-missing

test-all: test test-integration-gcp test-integration-aws

coverage-report:
	uv run coverage xml

test-resetup: setup test

lint:
	uv run ruff format --check src
	uv run ruff check src
	uv run pyright

fix:
	uv run ruff format src
	uv run ruff check --fix src
	uv run pyright

docs:
	# uv sync --extra docs # this blows up other dependencies / e.g. notebooks
	cd docs ; uv run mkdocs serve

kind:
	tools/setup_kind_cluster.sh

kind-teardown:
	kind delete cluster --name geneva

kuberay: kind
	tools/setup_kuberay.sh

kuberay11: kind
	KUBERAY_VERSION=1.1.0 tools/setup_kuberay.sh

notebook:
	uv pip install ipykernel ipywidgets
	uv run jupyter-notebook --ip=0.0.0.0
