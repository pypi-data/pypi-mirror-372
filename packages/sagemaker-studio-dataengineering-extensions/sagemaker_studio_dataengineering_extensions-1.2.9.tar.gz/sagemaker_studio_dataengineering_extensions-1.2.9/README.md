# SageMakerStudioDataEngineeringExtensions

SageMaker Unified Studio Data Engineering Extensions

This package contains several extensions that enhance the experiences for SageMakerStudioDataEngineeringSessions.

This pacakge is depend on SageMaker Unified Studio environment.

## List of extensions

- SageMaker Connection Magic JupyterLab Extension
- SageMaker Data Explorer
- SageMaker Jupyter Server Extension
- SageMaker Spark Monitor
- SageMaker Unified Studio Theme
- SageMaker UI Doc Manger JupyterLag Plugin

## How to install these extensions

### Conda
For Conda users, if you install this package via Conda, all of these extensions are installed by default.

### PyPi
For PyPi users, if you install this package via pip install,  all of these extensions are installed by default.

## Extension Details

### SageMaker Connection Magic JupyterLab Extension

This package contains a JupyterLab extension which provides a user-friendly experience for switching between different computes. For example, you can use this extension to easily switch from local python compute to different remote computes like EMR Cluster/Glue/EMR-Serverless.

### SageMaker Data Explorer

This package contains a JupyterLab extension which provides a side tab inside JupyterLab. That tab supports browsering data from different data source like Redshift/S3/LakeHouse.


### SageMaker Jupyter Server Extension

This package contains some Jupyter Server api to support other extensions in SageMaker Unified Studio.

### SageMaker Spark Monitor

This package contains a JupyterLab extension which provides a widget showing the progress of a running spark application in remote compute.

#### Setup

To load this extension, make sure you have iPython config file generated. If not, you could run `ipython profile create`, then a file with path `~/.ipython/profile_default/ipython_config.py` should be generated

Then you will need to add the following line in the end of that config file

```
c.InteractiveShellApp.extensions.extend(['sagemaker_sparkmonitor.kernelextension'])
```

once that config is added, restart the JupyterLab kernel to make the config change apply

### SageMaker Unified Studio Theme

This package contains a custom Theme for SageMaker Unified Studio

### SageMaker UI Doc Manger JupyterLag Plugin

This package is a JupyterLab extension which supports a shortcut from SageMaker Unified Studio portal to open a notebook in JupyterLab.
