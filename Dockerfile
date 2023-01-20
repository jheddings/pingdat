FROM python:3.11

RUN mkdir -p /opt/pingdat

COPY src poetry.lock pyproject.toml README.md /tmp/pingdat/
RUN pip3 install /tmp/pingdat/ && rm -Rf /tmp/pingdat

COPY etc/pingdat.yaml /opt/pingdat/

WORKDIR "/opt/pingdat"

USER root
EXPOSE 9056

# commands must be presented as an array, otherwise it will be launched
# using a shell, which causes problems handling signals for shutdown
ENTRYPOINT ["python3", "-m", "pingdat"]

# allow local callers to change the config file
CMD ["--config=/opt/pingdat/pingdat.yaml"]
