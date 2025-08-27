.PHONY: help lint lint/flake8 lint/black lint/isort lint/clang-tidy lint/clang-format format format/black format/autopep8 format/isort format/clang-format build/native build/wheel build test test/integration test/unit
.DEFAULT_GOAL := help

# C++ source files
CPP_FILES := $(shell find csrc -type f \( -name "*.cpp" -o -name "*.h" \) -not -path "*/third_party/*")

# Get pybind11 include path from the build directory
PYBIND11_DIR := $(shell find build/_deps/pybind11-src/include -type d 2>/dev/null)

lint/flake8: ## check style with flake8
	flake8 vidur

lint/black: ## check style with black
	black --check vidur

lint/isort: ## check style with isort
	isort --check-only --profile black vidur

lint: lint/black lint/isort lint/clang-format lint/clang-tidy ## check all style

lint/clang-tidy: ## check C++ style with clang-tidy
	test -f build/compile_commands.json || (echo "Please run CMake first to generate compile_commands.json" && exit 1)
	clang-tidy $(CPP_FILES) \
		-checks='-*,readability-*,modernize-*,cppcoreguidelines-*,performance-*,\
		-modernize-use-trailing-return-type,-readability-identifier-length' \
		-p build

lint/clang-format: ## check C++ format with clang-format
	clang-format -n -Werror $(CPP_FILES); \

format/black: ## format code with black
	black vidur

format/autopep8: ## format code with autopep8
	autopep8 --in-place --recursive vidur/

format/isort: ## format code with isort
	isort --profile black vidur

format: format/isort format/black format/clang-format ## format all code

format/clang-format: ## format C++ code with clang-format
	clang-format -i $(CPP_FILES); \

build/native:
	mkdir -p build && cd build \
	&& cmake -G Ninja -DCMAKE_BUILD_TYPE=Debug -DVIDUR_PYTHON_EXECUTABLE=`which python3` -DCMAKE_LIBRARY_OUTPUT_DIRECTORY=../vidur .. \
	&& cmake --build . --target default

build/wheel:
	python -m build --no-isolation --wheel
	python -m build --no-isolation --sdist

build: ## build the project
	pip install -e .

# === TESTING ===
##@ Testing

test: test/integration ## run all tests

test/integration: ## run integration tests
	python -m pytest test/integration/ -vvv --tb=long

test/unit: ## run unit tests (currently broken, placeholder for future fix)
	@echo "Unit tests are currently broken. Skipping..."
	@echo "To run when fixed: python -m pytest test/unit/ -v --tb=short"
