ARG BUILD_FROM
FROM ${BUILD_FROM}

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

ARG BUILD_ARCH
ARG VERSION
COPY rootfs /

RUN set -x && \
    apt-get install -y procps curl python3-pip && \
    pip3 install --trusted-host pypi.python.org -r /pwrstat/requirements.txt && \
    if [[ "${BUILD_ARCH}" = "amd64" ]]; \
        then apt-get install -y /PPL-1.3.3-64bit.deb; \
    fi && \
    if [[ "${BUILD_ARCH}" = "i386" ]]; \
        then apt-get install -y /PPL-1.3.3-32bit.deb; \
    fi && \
    apt-get -y --purge autoremove && apt-get clean && \
    rm -rf /tmp/* /var/tmp/* /var/lib/apt/lists/* \
        /PPL-1.3.3-64bit.deb /PPL-1.3.3-32bit.deb


# Build arguments
ARG BUILD_ARCH
ARG BUILD_DATE
ARG BUILD_DESCRIPTION
ARG BUILD_NAME
ARG BUILD_REF
ARG BUILD_REPOSITORY
ARG BUILD_VERSION

# Labels
LABEL \
    io.hass.name="${BUILD_NAME}" \
    io.hass.description="${BUILD_DESCRIPTION}" \
    io.hass.arch="${BUILD_ARCH}" \
    io.hass.type="addon" \
    io.hass.version=${BUILD_VERSION} \
    maintainer="Daniel Winks" \
    org.opencontainers.image.title="${BUILD_NAME}" \
    org.opencontainers.image.description="${BUILD_DESCRIPTION}" \
    org.opencontainers.image.authors="Daniel Winks" \
    org.opencontainers.image.licenses="Apache 2.0" \
    org.opencontainers.image.url="https://github.com/DanielWinks/HassOS-Addons" \
    org.opencontainers.image.source="https://github.com/DanielWinks/HassOS-Addons" \
    org.opencontainers.image.documentation="https://github.com/DanielWinks/HassOS-Addons/blob/main/README.md" \
    org.opencontainers.image.created=${BUILD_DATE} \
    org.opencontainers.image.revision=${BUILD_REF} \
    org.opencontainers.image.version=${BUILD_VERSION}