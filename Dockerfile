FROM python:3.11

RUN mkdir -p /opt/pingstats

COPY src poetry.lock pyproject.toml README.md /tmp/pingstats/
RUN pip3 install /tmp/pingstats/ && rm -Rf /tmp/pingstats

COPY etc/pingstats.yaml /opt/pingstats/

WORKDIR "/opt/pingstats"

USER root
EXPOSE 9056

# commands must be presented as an array, otherwise it will be launched
# using a shell, which causes problems handling signals for shutdown
ENTRYPOINT ["python3", "-m", "pingstats"]

# allow local callers to change the config file
CMD ["--config=/opt/pingstats/pingstats.yaml"]
