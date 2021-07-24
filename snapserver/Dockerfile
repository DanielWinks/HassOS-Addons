ARG BUILD_FROM

FROM ubuntu:hirsute as builder
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y \
    libasound2-dev \
    libpulse-dev \
    libvorbisidec-dev \
    libvorbis-dev \
    libopus-dev \
    libflac-dev \
    libsoxr-dev \
    alsa-utils \
    libavahi-client-dev \
    avahi-daemon \
    libexpat1-dev \
    wget \
    git \
    build-essential \
    pkg-config \
    meson g++ \
    libpcre3-dev \
    libmad0-dev \
    libmpg123-dev \
    libid3tag0-dev \
    libflac-dev \
    libvorbis-dev \
    libopus-dev \
    libogg-dev \
    libadplug-dev \
    libaudiofile-dev \
    libsndfile1-dev \
    libfaad-dev \
    libfluidsynth-dev \
    libgme-dev \
    libmikmod-dev \
    libmodplug-dev \
    libmpcdec-dev \
    libwavpack-dev \
    libwildmidi-dev \
    libsidplay2-dev \
    libsidutils-dev \
    libresid-builder-dev \
    libavcodec-dev \
    libavformat-dev \
    libmp3lame-dev \
    libtwolame-dev \
    libshine-dev \
    libsamplerate0-dev \
    libsoxr-dev \
    libbz2-dev \
    libcdio-paranoia-dev \
    libiso9660-dev \
    libmms-dev \
    libzzip-dev \
    libcurl4-gnutls-dev \
    libyajl-dev \
    libexpat-dev \
    libasound2-dev \
    libao-dev \
    libjack-jackd2-dev \
    libopenal-dev \
    libpulse-dev \
    libshout3-dev \
    libsndio-dev \
    libmpdclient-dev \
    libnfs-dev \
    libupnp-dev \
    libavahi-client-dev \
    libsqlite3-dev \
    libsystemd-dev \
    libgtest-dev \
    libboost-dev \
    libicu-dev \
    libchromaprint-dev \
    libgcrypt20-dev \
    libboost-dev \
    libboost-all-dev \
    npm


RUN wget -qOrustup.sh https://sh.rustup.rs
RUN sh rustup.sh -y
ENV PATH "/root/.cargo/bin:$PATH"

RUN git clone https://github.com/librespot-org/librespot.git
WORKDIR /librespot
RUN cargo build --release

WORKDIR /
RUN git clone https://github.com/badaix/snapcast.git
WORKDIR /snapcast
RUN make

WORKDIR /
RUN git clone https://github.com/badaix/snapweb.git
WORKDIR /snapweb
RUN npm install -g typescript
RUN make

RUN wget -qOmpd.tar.xz https://www.musicpd.org/download/mpd/0.22/mpd-0.22.9.tar.xz
RUN mkdir /mpd
RUN tar --strip-components=1 -xf mpd.tar.xz -C /mpd
WORKDIR /mpd
RUN meson . output/release --buildtype=debugoptimized -Db_ndebug=true
RUN meson configure output/release
RUN ninja -C output/release
RUN ninja -C output/release install


FROM ${BUILD_FROM}

RUN apt-get update && \
    apt-get dist-upgrade -y && \
    apt-get install -y \
    libasound2-dev \
    libpulse-dev \
    libvorbisidec-dev \
    libvorbis-dev \
    libopus-dev \
    libflac-dev \
    libsoxr-dev \
    alsa-utils \
    libavahi-client-dev \
    avahi-daemon \
    libexpat1-dev \
    libatomic1 \
    timidity

COPY --from=builder /librespot/target/release/librespot /usr/local/bin/librespot
COPY --from=builder /snapcast/server/snapserver /usr/local/bin/snapserver
COPY --from=builder /snapcast/client/snapclient /usr/local/bin/snapclient
COPY --from=builder /snapweb/dist/* /usr/share/snapserver/snapweb/
COPY --from=builder /mpd/output/release/mpd /usr/bin/mpd
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
