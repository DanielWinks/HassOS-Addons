ARG BUILD_FROM

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

COPY rootfs /
