ARG BUILD_FROM

FROM debian:stretch as builder

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
    pkg-config


RUN wget -qOrustup.sh https://sh.rustup.rs
RUN sh rustup.sh -y
ENV PATH "/root/.cargo/bin:$PATH"

RUN git clone https://github.com/librespot-org/librespot.git
WORKDIR /librespot
RUN cargo build --release

WORKDIR /
RUN wget -qOboost.tar.bz2 https://boostorg.jfrog.io/artifactory/main/release/1.76.0/source/boost_1_76_0.tar.bz2
RUN mkdir /boost
RUN tar --strip-components=1 -xf boost.tar.bz2 -C /boost
RUN git clone https://github.com/badaix/snapcast.git
WORKDIR /snapcast
RUN ADD_CFLAGS="-I/boost" make

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
    libatomic1

COPY --from=builder /librespot/target/release/librespot /usr/local/bin/librespot
COPY --from=builder /snapcast/server/snapserver /usr/local/bin/snapserver
COPY --from=builder /snapcast/client/snapclient /usr/local/bin/snapclient
COPY rootfs /

CMD [ "/run.sh" ]