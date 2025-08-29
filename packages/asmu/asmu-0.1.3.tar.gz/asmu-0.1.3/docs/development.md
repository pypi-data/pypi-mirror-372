# Development Tools

If you want to get into **asmu** development, this page is a great way to get you started and set up with the needed tools. Follow this guide and start developing your own **asmu** processors, expand them to your needs or update the documentation, examples or tests.

**Every contribution is welcome!**

## Get the source code

The first step is to clone the source code to your local machine. Make sure you have [git](https://git-scm.com/) installed and available in your terminal.
Then you can run
```sh
git git@gitlab.com:felhub/asmu.git
```
to clone the repository via ssh. Then use
```sh
cd asmu
```
to move inside the newly created project folder.

## Virtual environment

After installing [Python](https://www.python.org/) (we recommend the latest version, as it is usually the fastest), it is recommended to work within a virtual environment. 
This protects your local Python installation from becoming cluttered up with packages, especially on Unix based systems, which deploys with protected system Python.

To create a virtual environment call the following command in the projects root folder.
=== "Windows"
    ```sh
    python -m venv .venv
    ```
=== "Unix/macOS"
    ```sh
    python3 -m venv .venv
    ```

This creates a virtual environment in the folder `.venv`.
To enable your newly created environment, the system specific activate-script has to be called.

=== "Windows"
    ```powershell
    .venv\Scripts\activate
    ```
=== "Unix/macOS"
    ```bash
    source .venv/bin/activate
    ```

After successful activation your shell input line should start with `(.venv)`. To deactivate type
```sh
deactivate
```

## Install package locally

The first important step is to install the package in editable mode. This is done by using pip with the `-e` argument. Inside the packages root folder and with the activated virtual environment call
```sh
pip install -e .
```
This will install the **asmu** package locally, in addition to the required dependencies.
Depending on what you want to work on, you may require some optional dependencies.
These can be included in the local installation command with square brackets:

- `pip install -e .[check]` used for linting, typing and code style checks.
- `pip install -e .[test]` used for automated testing.
- `pip install -e .[docs]` used to build and deploy the documentation locally.
- `pip install -e .[profile]` installs the recommended tools for profiling

If you are unsure, it is recommended to install all packages with
```sh
pip install -e .[check,test,docs,profile]
```
for an effortless development experience :smile:.

## Build package

To prepare the package for distribution, it is built or packed into a specific form of archive. This is achieved with Pythons [build](https://pypi.org/project/build/) package. Usually, this is automatically handled by the GitLab pipeline for every new Tag. If you want to try it manually you first have to install or upgrade the build package with
```sh
python -m pip install --upgrade build
```
After that you can run
```sh
python -m build
```
in the root directory of the package.


## Documentation

The documentation is generated using [mkdocs-material](https://squidfunk.github.io/mkdocs-material) and automatically deployed for each commit by the GitLab pipeline to GitLab pages.
For the API section [mkdocstrings](https://mkdocstrings.github.io/) is used to parse the docstrings into an easy-to-read API documentation. If you want to build and deploy the documentation locally, you need to install the local packages with additional `docs` dependencies
```sh
pip install -e .[docs]
```
You can now host the documentation locally by running
```sh
mkdocs serve
```
which automatically updates for every save. View the documentation by opening the IP address returned by the command in your browser. To build the documentation run
```sh
mkdocs build -d .site --strict
```
The `--strict` argument is used to catch every warning. This also ensures that the pipeline will pass. It is important to specify a build directory with the `-d` argument, because the standard directory conflicts with the build package.

### Generating figures

Figures are automatically generated when `mkdocs` is started using a custom `on_startup()` hook. The hook is implemented in `mkdocs_hooks.py` and attached in the `mkdocs.yml`. Additionally, to the classic matplotlib figures, `pyreverse` (part of pylint) is used to generate structural diagrams of classes and packages. 

To generate the class graph as `.svg`, [graphviz](https://graphviz.org/) needs to be installed and in your path with
```sh
apt install -y graphviz
```

## Code style

Contributions to **asmu** should be as uniform as possible. Therefore, we deploy automated type and style checks in the GitLab pipeline. To check your code locally, make sure to install the **asmu** package with the correct additional dependencies with
```bash
pip install -e .[check]
```

The `mypy` package is used for automatic type checking. This excludes the `sounddevice` and `soundfile` package, as they don't provide any type specifications (settings are managed in the `pyproject.toml` file). On first run you need to install additional stubs with
```bash
mypy --install-types .
```
After confirming the installation, you can now use `mypy .` without the additional flags to test for missing types or mismatches.

Codestyle is checked according to [PEP8](https://peps.python.org/pep-0008/) using the `flake8` package. You can check the full project with
```sh
flake8 .
```

Import order is checked with `isort`. Using it with
```sh
isort . --check-only --diff 
```
checks all files for import order. Starting it without the flags automatically fixes the problems found.

Make sure all those tests run without errors, to avoid later conflicts in the GitLab pipeline

## Testing

The **asmu** package uses automatic test via [pytest](https://pypi.org/project/pytest/). The tests are located in the `tests` folder. To ensure the package's audio processors speeds are not negatively effected by changes to the code, the [pytest-benchamrk](https://pypi.org/project/pytest-benchmark/) plugin is used to monitor their execution times. There are no limiting values, but the execution times can be compared manually. The automatic tests run via the GitLab pipeline for every commit.

You can install the testing tools via
```bash
pip install -e .[test]
```
and run all tests, including a coverage test, with the command
```sh
- pytest --buffer --cov=asmu
```
where `--buffer` tests the different buffer settings, and `--cov=asmu` displays the coverage statistics.

## Profiling

When working on the audio core elements of the **asmu** package, it is very important to keep execution times and memory usage as low as possible. Memory assertions should be avoided. To achieve this, there are some recommended profiling tools where you can check your code line-by-line to optimize its performance. These profiling tools can be enabled for certain functions of your code, by wrapping them wit the `@profile` decorator.

Install the tools as optional dependencies when installing the **asmu** package locally with
```sh
pip install -e .[profile]
```

### line_profiler
The recommended profiler for execution times is the [line_profiler](https://pypi.org/project/line-profiler/). 
To profile your code, wrap the function(s) you want to analyze with the `@profile` decorator and run your script via
```sh
kernprof -l -v ./test.py
```

### memory_profiler
The [memory_profiler](https://pypi.org/project/memory-profiler/) can be used to analyze used and newly asserted memory. 
To profile your code, wrap the function(s) you want to analyze with the `@profile` decorator and run your script via
```sh
python -m memory_profiler ./test.py
```

!!! tip
    If try to run a script with a `@profile` decorator directly, this results in an error. To avoid this, you can find useful commands in the [`profiling.py`](examples.md#profilingpy) example.
