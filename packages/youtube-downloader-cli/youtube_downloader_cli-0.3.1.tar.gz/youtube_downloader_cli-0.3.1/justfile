set shell := ["/usr/bin/bash", "-c"]
PIP := "uv pip"
PACKAGE := "youtube-downloader-cli"
CMD := "youtube-downloader"
WHL := "$(find dist/ -name '*-any.whl')"
TESTPYPI_INDEX := "https://test.pypi.org/simple/"
PYPI_INDEX := "https://pypi.org/simple/"


[private]
default:
  just --list

# Run main command of the package
run *ARGS:
  uv run {{CMD}} {{ARGS}}

# Run linter and formatter
format:
  uvx ruff check --fix
  uvx ruff format

[private]
static-check:
  uvx ruff check
  uvx ruff format --check

# Clean & Build the package
[group('build')]
rebuild: clean build

# Build the package
[group('build')]
build: build-uv

[private]
build-uv:
  uv build --refresh

# Install all dependencies for development
[group('initialize')]
init: clean init-dev install-tool

[private]
init-dev:
  uv sync --refresh --extra dev --no-install-project

[private]
install-tool:
  uv tool install ruff -U --refresh
  uv tool install bump-my-version -U --refresh

# Clean virtualenv and build artifacts
[group('clean')]
clean:
  rm -rf dist/
  rm -rf .venv/
  rm -rf $(find -name '*.egg-info')
  rm -rf $(find -name '__pycache__')

# Upload package to TestPyPI (target=test) or PyPI (target=PyPI)
[group('pypi')]
upload target: static-check rebuild
  #!/usr/bin/bash
  if [[ {{target}} == "test" ]]; then
    set -x ; uvx uv-publish --repository testpypi
  elif [[ {{target}} == "pypi" ]]; then
    set -x ; uvx uv-publish --repository pypi
  fi

# Install package from TestPyPI (target=test) or PyPI (target=PyPI - default)
[group('pypi')]
install target="pypi":
  #!/usr/bin/bash
  if [[ {{target}} == "test" ]]; then
    set -x ; uv tool install {{PACKAGE}} -U --reinstall --index {{TESTPYPI_INDEX}} --index-url {{PYPI_INDEX}}
  elif [[ {{target}} == "pypi" ]]; then
    set -x ; uv tool install {{PACKAGE}} -U --reinstall
  fi

# Show bump version
[group('bump-version')]
show-bump:
  uvx bump-my-version show-bump

# Bump version
[group('bump-version')]
bump *ARGS:
  uvx bump-my-version bump {{ARGS}}
  @echo "new version $(cat $(find -name VERSION))"

# Create virtualenv with package installed
[group('local-testing')]
make-testing: rebuild
  #!/usr/bin/bash
  source $(which virtualenvwrapper.sh)
  echo mkvirtualenv -i {{WHL}} --clear yt-dl-cli-testing 
  mkvirtualenv -i {{WHL}} --clear yt-dl-cli-testing

# Remove created virtualenv
[group('local-testing')]
remove-testing:
  #!/usr/bin/bash
  source $(which virtualenvwrapper.sh)
  echo rmvirtualenv yt-dl-cli-testing
  rmvirtualenv yt-dl-cli-testing

