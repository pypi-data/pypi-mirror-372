# Making a new release of sagemaker_ui_doc_manager_jl_plugin

## Manual release

### Building the tarball

This extension can be distributed as Python packages. All of the Python packaging instructions in the `pyproject.toml`
file to wrap your extension in a Python package. Before generating a package, we first need to install `build`.

Bump the version in `package.json` and `meta.yaml`

Make sure to clean up all the development files before building the package:

```bash
bb clean:all
```

You could also clean up the local git repository:

```bash
git clean -dfX
```

To create a Python source package (`.tar.gz`) and the binary package (`.whl`) in the `dist/` directory, do:

```bash
python -m build
```

To create a conda package (`.tar.bz2`), do:

```bash
conda build .
```

### Adding tarball to SageMaker Distribution (SMD)

In order to add a new tarball to SMD, follow the steps documented
[here](https://quip-amazon.com/gq2dAtOo0FL2/MaxDome-components-in-SageMaker-distribution#temp:C:ZER3ed8eb502e4c4b2ab6f3ab0b5).
