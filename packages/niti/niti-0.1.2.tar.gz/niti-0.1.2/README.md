# Niti by Vajra 

Fast, Modern, Lean Linter for C++ code for Vajra. Easy to configure no frills supercharged C++ linter.

A simple extensible C++ linter written in Python allowing custom rules.

## Setup

Right now Niti is not available on PyPi. See [Development](#option-1-using-uv-recommended) to install from source.

## Development

### Prerequisites

- Python 3.8 or higher

### Setting Up Development Environment

We recommend using a virtual environment to isolate dependencies. You can use either `uv` or `conda`:

#### Option 1: Using uv (Recommended)
```bash
# Clone the repository
git clone https://github.com/project-vajra/niti.git
cd niti

# Create and activate virtual environment with uv
uv venv
source .venv/bin/activate 

# Install dependencies
# For development:
uv pip install -r requirements-dev.txt
# Install Niti
uv pip install -e .

# Or install directly with optional dependencies:
uv pip install -e .[dev]
```

#### Option 2: Using conda/mamba
```bash
# Clone the repository
git clone https://github.com/project-vajra/niti.git
cd niti

# Create conda environment from file
conda env create -f environment.yml
conda activate niti

# Install the package in editable mode
pip install -e .

# Or use the Makefile for convenience
make install-dev
```

### Installing Dependencies

The project has the following main dependencies:
- `pyyaml`: For configuration file parsing
- `tree-sitter` & `tree-sitter-cpp`: For C++ code parsing

Development dependencies include:
- `pytest`: Testing framework
- `black`, `isort` & `autoflake`: Code formatting and cleanup
- `flake8` & `mypy`: Linting and type checking
- `pytest-cov`: Coverage reporting

**Note**: Niti is not yet available on PyPI. For now, please install from source as shown above.

### Using Niti

#### Running the Linter

Once installed, you can run Niti on any C++ project:

```bash
# Lint a single file
niti path/to/your/file.cpp

# Lint an entire directory
niti path/to/your/cpp/project/

# Lint current directory
niti .

# Show help and available options
niti --help
```

#### Configuration

Niti can be configured using a `.nitirc` file or command-line options. See the examples section for configuration samples.

### Development Workflow

#### Running Tests using PyTests

Niti has a comprehensive test suite organized into unit and integration tests:

```bash
# Run all tests
pytest

# Run all tests with coverage report
pytest --cov=niti --cov-report=html

# Run only unit tests (fast, isolated)
pytest -m unit

# Run only integration tests (slower, end-to-end)
pytest -m integration

# Run tests for specific rule categories
pytest test/unit/naming/           # Naming convention rules
pytest test/unit/safety/           # Safety rules
pytest test/unit/modern_cpp/       # Modern C++ rules
pytest test/unit/documentation/    # Documentation rules

# Run tests with verbose output
pytest -v

# Run a specific test file
pytest test/unit/types/test_type_rules.py

# Run a specific test method
pytest test/unit/naming/test_naming_rules.py::TestNamingFunctionCase::test_detects_snake_case_functions
```

##### Using the Custom Test Runner

The project includes a custom test runner for convenience:

```bash
# Run unit tests
python test/run_tests.py unit

# Run integration tests
python test/run_tests.py integration

# Run all tests
python test/run_tests.py all

# Run with verbose output and coverage
python test/run_tests.py unit -v -c
```

##### Test Structure

The test suite is organized as follows:
- **`test/unit/`**: Fast, isolated unit tests organized by rule category
- **`test/integration/`**: End-to-end integration tests
- **`test/fixtures/`**: Reusable C++ code samples for testing
- **`test/test_utils.py`**: Base classes and testing utilities

Each rule category has comprehensive positive (should pass) and negative (should fail) test cases using real C++ code examples.

#### Code Quality Checks

You can use individual commands or the convenient Makefile targets:

##### Using Makefile (Recommended)
```bash
# Format code (autoflake + black + isort)
make format

# Run linting (flake8 + mypy)
make lint

# Run tests
make test

# Run tests with coverage
make test-cov

# Show all available commands
make help
```

#### Project Structure
```
niti/
├── niti/                   # Main package
│   ├── cli.py             # Command-line interface
│   ├── core/              # Core functionality
│   │   ├── config.py      # Configuration handling
│   │   ├── engine.py      # Linting engine
│   │   ├── issue.py       # Issue representation
│   │   └── severity.py    # Severity levels
│   └── rules/             # Linting rules (54+ rules across categories)
│       ├── base.py        # Base rule classes
│       ├── naming.py      # Naming convention rules
│       ├── safety.py      # Safety-related rules
│       ├── modern_cpp.py  # Modern C++ best practices
│       ├── documentation.py # Documentation requirements
│       ├── types.py       # Type system rules
│       └── ...            # Other rule categories
├── test/                  # Comprehensive test suite
│   ├── unit/              # Unit tests by rule category
│   │   ├── naming/        # Tests for naming rules
│   │   ├── safety/        # Tests for safety rules
│   │   ├── modern_cpp/    # Tests for modern C++ rules
│   │   ├── documentation/ # Tests for documentation rules
│   │   ├── types/         # Tests for type system rules
│   │   └── ...            # Other rule category tests
│   ├── integration/       # End-to-end integration tests
│   ├── fixtures/          # Reusable C++ code samples
│   ├── test_utils.py      # Testing base classes and utilities
│   └── run_tests.py       # Custom test runner
├── pyproject.toml         # Project configuration
├── Makefile              # Development workflow commands
├── CLAUDE.md             # Claude Code assistant guidance or for other Agentic tools
└── README.md             # This file
```

## Examples

Full sample on using the Linter in a large-scale C++ project in the Vajra project will be out soon. We're building [Vajra](https://github.com/project-vajra/vajra) the second-generation LLM serving engine in C++. Watch out this space for more details soon.

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.