# Default recipe, list the available recipes
default:
    @just --list

# Delete temporary artifacts
clean:
    @rm -rfv dist build *.egg-info

# Builds the wheel package
wheel: clean
    @python -m build --wheel

# Install the development requirements
install-dev:
    @uv pip install -r requirements-dev.txt

# Update all the requirements files from the .in files
requirements:
    @uv pip compile -q requirements-build.in -o requirements-build.txt
    @uv pip compile -q requirements-lint.in -o requirements-lint.txt
    @uv pip compile -q requirements-dev.in -o requirements-dev.txt

# Upgrade a single requirement to the latest version
upgrade-requirements +names:
    @uv pip compile -q requirements-build.in -o requirements-build.txt -P {{replace(names, " ", " -P ")}}
    @uv pip compile -q requirements-lint.in -o requirements-lint.txt -P {{replace(names, " ", " -P ")}}
    @uv pip compile -q requirements-dev.in -o requirements-dev.txt -P {{replace(names, " ", " -P ")}}
