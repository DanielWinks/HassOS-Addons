ARG BUILD_FROM

# Build binaries
FROM ${BUILD_FROM} as builder

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN \
    apt-get update \
    && \
    apt-get dist-upgrade -y \
    && \
    apt-get install -y \
    alsa-utils \
    avahi-daemon \
    build-essential \
    git \
    libasound2-dev \
    libavahi-client-dev \
    libexpat1-dev \
    libflac-dev \
    libopus-dev \
    libpulse-dev \
    libsoxr-dev \
    libvorbis-dev \
    libvorbisidec-dev \
    wget


RUN wget -qOrustup.sh https://sh.rustup.rs
RUN sh rustup.sh -y
RUN source $HOME/.cargo/env
RUN git clone https://github.com/librespot-org/librespot.git
WORKDIR /librespot
RUN $HOME/.cargo/bin/cargo build --release --no-default-features --features "with-dns-sd"

WORKDIR /
RUN wget -qOboost.tar.bz2 https://boostorg.jfrog.io/artifactory/main/release/1.76.0/source/boost_1_76_0.tar.bz2
RUN mkdir /boost
RUN tar --strip-components=1 -xf boost.tar.bz2 -C /boost
RUN git clone https://github.com/badaix/snapcast.git
WORKDIR /snapcast
RUN ADD_CFLAGS="-I/boost" make

# Build image
FROM ${BUILD_FROM}

RUN \
    apt-get update \
    && \
    apt-get dist-upgrade -y \
    && \
    apt-get install -y \
    alsa-utils \
    avahi-daemon \
    gstreamer1.0-tools \
    libasound2-dev \
    libatomic1 \
    libavahi-client-dev \
    libexpat1-dev \
    libflac-dev \
    libopus-dev \
    libpulse-dev \
    libsoxr-dev \
    libvorbis-dev \
    libvorbisidec-dev \
    python3-pip \
    sox \
    && \
    pip3 install -r \
    rootfs/tts/requirements.txt

COPY --from=builder /librespot/target/release/librespot /usr/bin/librespot
COPY --from=builder /snapcast/server/snapserver /usr/bin/snapserver
COPY --from=builder /snapcast/client/snapclient /usr/bin/snapclient

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
