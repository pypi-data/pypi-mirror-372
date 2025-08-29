FROM 31z4/tox:4-3.0

USER root

RUN set -eux; \
    apt-get update; \
    DEBIAN_FRONTEND=noninteractive \
    apt-get install -y --no-install-recommends \
        curl; \
    rm -rf /var/lib/apt/lists/*

# Download and install Docker CLI - required for integration tests
RUN curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh

WORKDIR /sdk/python

USER tox
