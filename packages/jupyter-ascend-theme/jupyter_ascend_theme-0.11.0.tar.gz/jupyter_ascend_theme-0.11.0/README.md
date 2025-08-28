# jupyter_ascend_theme <https://pypi.org/project/jupyter-ascend-theme/>

The JupyterLab ASCEND theme.
An extension for JupyterLab, published as a PIP package, adds two ASCEND-branded themes (light and dark) and some UI elements.

This project was initialized using a copier template for Jupyterlab extensions: <https://github.com/jupyterlab/extension-template>.

## Development Requirements

To initialize a working development environment, ensure you have the following installed on your machine:

- Node
- npm
- Yarn
- pip
- Python
- JupyterLab

The tested development environment uses the following versions:

- Node: 20.12.2
- npm: 10.5.0
- pip: 24.2
- Python: 3.11.3
- JupyterLab: 4.2.4

The template used to create this extension suggests using:

- JupyterLab >= 4.0.0

## Install the published package (production use)

⚠️ **Note:** Your extensions may break with new releases of JupyterLab. As noted in Backwards Compatibility, Versions and Breaking Changes, JupyterLab development and release cycles follow semantic versioning, so we recommend planning your development process to account for possible future breaking changes that may disrupt users of your extensions. Consider documenting your maintenance plans to users in your project, or setting an upper bound on the version of JupyterLab your extension is compatible with in your project’s package metadata.

<https://jupyterlab.readthedocs.io/en/stable/extension/extension_dev.html>

To install the extension, execute:

```bash
pip install jupyter_ascend_theme
```

## Uninstall

To remove the extension, execute:

```bash
pip uninstall jupyter_ascend_theme
```

## Development

### Development install

Note: You will need NodeJS to build the extension package.

The `jlpm` command is JupyterLab's pinned version of [yarn](https://yarnpkg.com/) that is installed with JupyterLab.

You may use `yarn` or `npm` instead of `jlpm` below.

```bash
# Clone the repository to your local environment
git clone https://gitlab.dev.eoss-cloud.it/cgi-italy/poieo/uis/jupyter-ascend-theme.git

# Change directory to the repository directory
cd jupyter-ascend-theme

# Install python packages in development mode
pip install -e "."

# Install js packages
jlpm install

# Link your development version of the extension with JupyterLab
jupyter labextension develop . --overwrite

# Rebuild extension Typescript source after making changes
jlpm build
```

You can watch the source directory and run JupyterLab simultaneously in different terminals to watch for changes in the extension's source and automatically rebuild the extension.

```bash
# Watch the source directory in one terminal, automatically rebuilding when needed
jlpm watch

# Run JupyterLab in another terminal
jupyter lab
```

With the watch command running, every saved change will immediately be built locally and available in your running JupyterLab. Refresh JupyterLab to load the change in your browser (you may need to wait several seconds for the extension to be rebuilt).

By default, the `jlpm build` command generates the source maps for this extension to make it easier to debug using the browser dev tools. To also generate source maps for the JupyterLab core extensions, you can run the following command:

```bash
jupyter lab build --minimize=False
```

### Development uninstall

```bash
pip uninstall jupyter_ascend_theme
```

In development mode, you will also need to remove the symlink created by the `jupyter labextension develop` command. To find its location, you can run `jupyter labextension list` to figure out where the `labextensions` folder is located. Then you can remove the symlink named `jupyter-ascend-theme` within that folder.

## Packaging and releasing the extension

See [RELEASE](RELEASE.md)
