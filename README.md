# wxdat #

[![PyPI](https://img.shields.io/pypi/v/pingstat.svg)](https://pypi.org/project/pingstat)
[![LICENSE](https://img.shields.io/github/license/jheddings/pingstat)](LICENSE)
[![Style](https://img.shields.io/badge/style-black-black)](https://github.com/ambv/black)

A Prometheus exporter for ping statistics.

## Installation ##

Install the published package using pip:

```shell
pip3 install pingstat
```

This project uses `poetry` to manage dependencies and a local virtual environment.  To
get started, clone the repository and install the dependencies with the following:

```shell
poetry pingstat
```

## Usage ##

Run the module and tell it which config file to use.

```shell
python3 -m pingstat --config pingstat.yaml
```

If you are using `poetry` to manage the virtual environment, use the following:

```shell
poetry run python -m pingstat --config pingstat.yaml
```

## Configuration ##
