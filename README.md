# wxdat #

[![PyPI](https://img.shields.io/pypi/v/pingstats.svg)](https://pypi.org/project/pingstats)
[![LICENSE](https://img.shields.io/github/license/jheddings/pingstats)](LICENSE)
[![Style](https://img.shields.io/badge/style-black-black)](https://github.com/ambv/black)

A Prometheus exporter for ping statistics.

## Installation ##

Install the published package using pip:

```shell
pip3 install pingstats
```

This project uses `poetry` to manage dependencies and a local virtual environment.  To
get started, clone the repository and install the dependencies with the following:

```shell
poetry pingstats
```

## Usage ##

Run the module and tell it which config file to use.

```shell
python3 -m pingstats --config pingstats.yaml
```

If you are using `poetry` to manage the virtual environment, use the following:

```shell
poetry run python -m pingstats --config pingstats.yaml
```

## Configuration ##

For now, review the sample `pingstats.yaml` config file for a description of supported
configuration options.
