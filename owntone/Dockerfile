ARG BUILD_FROM

FROM ${BUILD_FROM}

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

VOLUME /etc/localtime:/etc/localtime:ro

RUN \
    mkdir -p /usr/share/man/man1 \
    && \
    apt-get update \
    && \
    apt-get install -y --fix-missing --no-install-recommends \
    antlr3 \
    autoconf \
    automake \
    autotools-dev \
    build-essential \
    gawk \
    gettext \
    git \
    gperf \
    libantlr3c-dev \
    libasound2-dev \
    libavahi-client-dev \
    libavcodec-dev \
    libavfilter-dev \
    libavformat-dev \
    libavutil-dev \
    libconfuse-dev \
    libcurl4-openssl-dev \
    libevent-dev \
    libgcrypt20-dev \
    libjson-c-dev \
    libmxml-dev \
    libplist-dev \
    libprotobuf-c-dev \
    libsodium-dev \
    libsqlite3-dev \
    libswscale-dev \
    libtool \
    libunistring-dev \
    libwebsockets-dev \
    zlib1g-dev \
    && \
    apt-get -y --purge autoremove \
    && \
    apt-get clean \
    && \
    rm -rf /tmp/* /var/tmp/* /var/lib/apt/lists/*

RUN cd /tmp && \
    git clone https://github.com/owntone/owntone-server.git && \
    cd /tmp/owntone-server && \
    autoreconf -fi && \
    ./configure \
    --with-libwebsockets \
    --disable-spotify \
    --disable-lastfm \
    --disable-webinterface \
    && \
    make && \
    make install


RUN cd /usr/local/etc \
    && sed -i -e 's/\(uid.*=.*\)/uid = "root"/g' owntone.conf \
    && sed -i s#"ipv6 = yes"#"ipv6 = no"#g owntone.conf \
    && sed -i s#/srv/music#/config/owntone/music#g owntone.conf \
    && sed -i s#/usr/local/var/cache/owntone/songs3.db#/config/owntone/cache/songs3.db#g owntone.conf \
    && sed -i s#/usr/local/var/cache/owntone/cache.db#/config/owntone/cache/cache.db#g owntone.conf \
    && sed -i s#/usr/local/var/log/owntone.log#/dev/stdout#g owntone.conf \
    && sed -i "/websocket_port\ =/ s/# *//" owntone.conf \
    && sed -i "/trusted_networks\ =/ s/# *//" owntone.conf \
    && sed -i "/pipe_autostart\ =/ s/# *//" owntone.conf \
    && sed -i "/db_path\ =/ s/# *//" owntone.conf \
    && sed -i "/cache_path\ =/ s/# *//" owntone.conf

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
