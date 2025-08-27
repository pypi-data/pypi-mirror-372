# Making a new release of sagemaker_connection_magics_jlextension

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

To build from scratch:
```bash
brazil-build
rm -r build
npm run clean && npm run build:lib:prod && npm run build:labextension && python -m build
```

To create a conda package (`.tar.bz2`), please:
1. Follow the instruction of "build from scratch"
2. Make sure you delete /node_module, /dist and /lib folder
3. follow: https://quip-amazon.com/ioJ9AHg9owIK/Conda-packages-build and run ```conda build . --python 3.11 && conda build . --python 3.12```
4. If you are building on Mac, run conda convert to convert the platform to linux
5. After building, please try to install the bz2 file on a MaxDome space using conda install ****.bz2

### Adding tarball to SageMaker Distribution (SMD)

In order to add a new tarball to SMD, follow the steps documented
[here](https://quip-amazon.com/gq2dAtOo0FL2/MaxDome-components-in-SageMaker-distribution#temp:C:ZER3ed8eb502e4c4b2ab6f3ab0b5).



### Testing the plugin on the SMD JupyterLab
After installing sagemaker_dataenginnering_extensions, 

* Open JupyterLab Settings -> Theme and verify that the `Amazon SageMaker Unified Studio Dark` shows up as an option
* Also verify that the `Amazon SageMaker Unified Studio Dark` is the default theme selected.