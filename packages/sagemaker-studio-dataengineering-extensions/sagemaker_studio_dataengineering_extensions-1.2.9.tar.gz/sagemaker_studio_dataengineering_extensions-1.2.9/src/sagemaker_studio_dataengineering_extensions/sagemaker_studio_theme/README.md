# MaxDomeThemeJLPlugin

## Requirements

- JupyterLab >= 4.0

## Install

To install the extension, execute:

```bash
pip install sagemaker_ui_theme
```

## Uninstall

To remove the extension, execute:

```bash
pip uninstall sagemaker_ui_theme
```

## Contributing

### Development install

Note: You will need NodeJS to build the extension package.

```bash
# Clone the repo to your local environment
# Change directory to the sagemaker_ui_theme directory
# Install package in development mode
bb
pip3 install -e "." --break-system-packages
# Link your development version of the extension with JupyterLab
jupyter labextension develop . --overwrite
```

You can watch the source directory and run JupyterLab at the same time in different terminals to watch for changes in
the extension's source and automatically rebuild the extension.

```bash
# Watch the source directory in one terminal, automatically rebuilding when needed
bb watch
# Run JupyterLab in another terminal
jupyter lab
```

With the watch command running, every saved change will immediately be built locally and available in your running
JupyterLab. Refresh JupyterLab to load the change in your browser (you may need to wait several seconds for the
extension to be rebuilt).

By default, the `npm run build` command generates the source maps for this extension to make it easier to debug using
the browser dev tools. 

To also generate source maps for the JupyterLab core extensions, you can run the following
command:

```bash
jupyter lab build --minimize=False
```

### Development uninstall

```bash
pip uninstall sagemaker_ui_theme
```

In development mode, you will also need to remove the symlink created by `jupyter labextension develop` command. To find
its location, you can run `jupyter labextension list` to figure out where the `labextensions` folder is located. Then
you can remove the symlink named `sagemaker-ui-theme-jlplugin` within that folder.

### Packaging the extension

See [RELEASE](RELEASE.md)
