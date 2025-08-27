# sagemaker_jupyter_server_extension

A JupyterLab extension for SageMaker.
This extension is composed of a Python package named `sagemaker_jupyter_server_extension`


## Troubleshoot

Check that the server extension is enabled:

```bash
jupyter server extension list
```

Enable the server extension:

```bash
jupyter server extension enable sagemaker_jupyter_server_extension
```

Disable the extension:
```bash
jupyter server extension disable sagemaker_jupyter_server_extension
```

Or you can use the command line to enable/disable the extension:
```bash
jupyter lab  --ServerApp.jpserver_extensions="sagemaker_jupyter_server_extension=True"
```

## Contributing

### Development install

You can directly make changes to this package, build it and then run it with JupyterLab.

Please make sure you have jupyter installed in you machine already.

```bash
# Clone the repo to your local environment
# Change directory to the sagemaker_jupyter_server_extension directory
# Make code changes
# Install package in development mode
pip install -e .
# Server extension must be manually installed in develop mode
jupyter server extension enable sagemaker_jupyter_server_extension
# Start the Jupyter
jupyter lab
# verify you have the following output in the log and the extension should be loaded
sagemaker_jupyter_server_extension | extension was successfully loaded.
```

You can also call the ```/sagemaker/ping``` API and verify the extension is successfully installed.

### Development uninstall

```bash
# Server extension must be manually disabled in develop mode
jupyter server extension disable sagemaker_jupyter_server_extension
pip uninstall sagemaker_jupyter_server_extension
```

### Testing the extension

#### Server tests

This extension is using [Pytest](https://docs.pytest.org/) for Python code testing.

Install test dependencies (needed only once):

```sh
pip install -e ".[test]"
```

To execute them, run:

```sh
sudo pytest -vv -r ap sagemaker_jupyter_server_extension
```


### Test conda build
1. Please have conda installed. You can run ```conda help``` to make sure.
2. Please go to the root directory of this project, and run ```conda build .```
```sh
cd ~/workplace/SageMakerJupyterServerExtension/
conda build .
```
3. Verify the ```bz``` file is generated. Please go to your local channel folder, based on your platform (osx/linux), you will find a .bz file named ```sagemaker_jupyter_server_extension-0.1.0-py310_0.tar.bz2``` that is newly created. For example, for me, my file is under ```/Users/username/miniforge3/conda-bld/osx-arm64/```
4. Verify conda install by running ```conda install --use-local sagemaker_jupyter_server_extension```

### Local build
https://quip-amazon.com/ioJ9AHg9owIK/Conda-packages-build

### Releasing the extension
```angular2html
- Go to buildspec.yml and modify the RELEASE_VERSION to the corresponding release label. Submit a CR for the commit to release the change.
- Artifacts will be generated to prod-maxdome-dataengineering-artifacts-us-west-2 s3 bucket in Hemingway release account. 
- Using 2P rule to enable promotion to PublishToSMD stage in sagemaker-spark-monitor-widget CodePipeline in Hemingway release account, and artifacts will be published to SMD repo.
- Disable the promotion again to avoid multiple release to SMD.
```

