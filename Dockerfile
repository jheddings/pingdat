FROM python:3.13

COPY src poetry.lock pyproject.toml README.md /tmp/pingdat/
RUN pip3 install /tmp/pingdat/ && rm -Rf /tmp/pingdat

COPY etc/pingdat.yaml /etc/pingdat.yaml

USER root
EXPOSE 9056

# commands must be presented as an array, otherwise it will be launched
# using a shell, which causes problems handling signals for shutdown
ENTRYPOINT ["python3", "-m", "pingdat"]

# allow local callers to change the config file
CMD ["--config=/etc/pingdat.yaml"]
