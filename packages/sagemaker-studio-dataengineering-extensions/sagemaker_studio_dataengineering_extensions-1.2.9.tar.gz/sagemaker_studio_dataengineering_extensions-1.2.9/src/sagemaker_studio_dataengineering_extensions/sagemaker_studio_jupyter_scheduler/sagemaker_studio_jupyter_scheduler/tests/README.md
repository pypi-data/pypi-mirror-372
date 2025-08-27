By default, this package is configured to run PyTest tests
(http://pytest.org/).

## Writing tests

Place test files in this directory, using file names that start with `test_`.

## Running tests
### Using `brazil`
```
$ brazil-build test
```

To configure pytest's behaviour in a single run, you can add options using the --addopts flag:

```
$ brazil-build test --addopts="[pytest options]"
```

For example, to run a single test, or a subset of tests, you can use pytest's
options to select tests:

```
$ brazil-build test --addopts="-k TEST_PATTERN"
```

Code coverage is automatically reported for sage_maker_scheduling_jupyter_server_extension;
to add other packages, modify setup.cfg in the package root directory.

To debug the failing tests:

```
$ brazil-build test --addopts=--pdb
```

This will drop you into the Python debugger on the failed test.

### Using `pytest`
```
# Build the package using the `release` target
$ brazil-build release

# Install the project in editable mode if required
$ pip install -e ".[dev]"

# In the root folder, run this command to trigger all unit tests 
$ pytest . 
```
