ARG BUILD_FROM

FROM ${BUILD_FROM}

RUN \
    apk --update upgrade && \
    apk add --no-cache \
    avahi \
    gst-libav \
    gstreamer \
    gstreamer-dev \
    gst-plugins-base \
    gst-plugins-good \
    gst-plugins-bad \
    gst-plugins-ugly \
    nginx \
    py3-gst \
    py3-pip \
    snapcast \
    && \
    apk add \
    librespot --repository=http://dl-cdn.alpinelinux.org/alpine/edge/testing \
    && \
    rm -rf /var/cache/apk/*
# && \
# python3 -m pip install \
# Mopidy-Iris \
# Mopidy-Local \
# Mopidy-MPD

COPY rootfs /

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
    maintainer="Daniel Winks <daniel.winks@gmail.com>" \
    org.opencontainers.image.title="${BUILD_NAME}" \
    org.opencontainers.image.description="${BUILD_DESCRIPTION}" \
    org.opencontainers.image.vendor="Daniel's Home Assistant Add-ons" \
    org.opencontainers.image.authors="Daniel Winks <daniel.winks@gmail.com>" \
    org.opencontainers.image.licenses="Apache" \
    org.opencontainers.image.url="https://github.com/DanielWinks/HassOS-Addons" \
    org.opencontainers.image.source="https://github.com/${BUILD_REPOSITORY}" \
    org.opencontainers.image.documentation="https://github.com/${BUILD_REPOSITORY}/blob/main/README.md" \
    org.opencontainers.image.created=${BUILD_DATE} \
    org.opencontainers.image.revision=${BUILD_REF} \
    org.opencontainers.image.version=${BUILD_VERSION}
