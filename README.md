# pingdat #

[![PyPI](https://img.shields.io/pypi/v/pingdat.svg)](https://pypi.org/project/pingdat)
[![LICENSE](https://img.shields.io/github/license/jheddings/pingdat)](LICENSE)
[![Style](https://img.shields.io/badge/style-black-black)](https://github.com/ambv/black)

A Prometheus exporter for ping statistics.

## Installation ##

Install the published package using pip:

```shell
pip3 install pingdat
```

This project uses `poetry` to manage dependencies and a local virtual environment.  To
get started, clone the repository and install the dependencies with the following:

```shell
poetry install
```

### Grafana Dashboard ###

A Grafana dashboard is available as #(17922)[https://grafana.com/grafana/dashboards/17922].

## Usage ##

Run the module and tell it which config file to use.

```shell
python3 -m pingdat --config pingdat.yaml
```

If you are using `poetry` to manage the virtual environment, use the following:

```shell
poetry run pingdat --config pingdat.yaml
```

### Docker ###

`pingdat` is available as a published Docker image.  To run, use the latest version:
from Docker Hub:

```shell
docker container run --rm --publish 9056:9056 "jheddings/pingdat:latest"
```

The configuration file is read from `/opt/pingdat/pingdat.yaml` and may be changed
with arguments to the container:

```shell
docker container run --rm --tty --publish 9056:9056 \
  --volume "/path/to/host/config:/etc/pingdat" \
  "jheddings/pingdat:latest" --config /etc/pingdat/pingdat.yaml
```

## Docker Compose ##

A sample configuration is also provided for using `docker compose`.  Similar to using
Docker directly, the configuration file can be provided on the host side.  Then,
simply start the cluster normally:

```shell
docker compose up
```

Or detached as a background process:

```shell
docker compose up --detach
```

## Configuration ##

For now, review the sample `pingdat.yaml` config file for a description of supported
configuration options.
