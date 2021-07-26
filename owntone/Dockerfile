ARG BUILD_FROM

FROM ${BUILD_FROM} as base
ARG BUILD_ARCH

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

VOLUME /etc/localtime:/etc/localtime:ro

ENV BUILD_DEPS \
    autoconf \
    automake \
    autotools-dev \
    build-essential \
    git \
    libantlr3c-dev \
    libasound2-dev \
    libavahi-client-dev \
    libavcodec-dev \
    libavfilter-dev \
    libavformat-dev \
    libavutil-dev \
    libconfuse-dev \
    libcurl4-gnutls-dev \
    libevent-dev \
    libgcrypt20-dev \
    libgnutls28-dev \
    libjson-c-dev \
    libmxml-dev \
    libplist-dev \
    libplist-dev \
    libprotobuf-c-dev \
    libpulse-dev \
    libsodium-dev \
    libsqlite3-dev \
    libswscale-dev \
    libtool \
    libunistring-dev \
    libwebsockets-dev \
    openjdk-11-jre-headless \
    zlib1g-dev

ENV RUN_DEPS \
    libantlr3c-3.4-0 \
    libasound2 \
    libavahi-client3 \
    libavcodec58 \
    libavfilter7 \
    libavformat58 \
    libavutil56 \
    libconfuse2 \
    libcurl3-gnutls \
    libevent-2.1-6 \
    libevent-pthreads-2.1-6 \
    libgcrypt20 \
    libgnutls30 \
    libjson-c3 \
    libmxml1 \
    libplist3 \
    libprotobuf-c1 \
    libpulse0 \
    libsodium23 \
    libsqlite3-0 \
    libswscale5 \
    libunistring2 \
    libwebsockets8 \
    nginx \
    zlib1g \
    avahi-daemon

RUN apt-get update -y \
    && \
    apt-get install -y --no-install-recommends \
    curl \
    gpg \
    gpg-agent \
    dirmngr \
    apt-transport-https \
    gawk \
    gettext \
    gperf \
    && \
    rm -rf /var/lib/apt/lists/*

RUN if [ ! "$BUILD_ARCH" = "aarch64" ] ; then \
    curl -L https://apt.mopidy.com/mopidy.list -o /etc/apt/sources.list.d/mopidy.list \
    && curl -L https://apt.mopidy.com/mopidy.gpg -o /tmp/mopidy.gpg \
    && apt-key add /tmp/mopidy.gpg; \
    fi

FROM base AS builder
ARG BUILD_ARCH
RUN mkdir -p /usr/share/man/man1
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    ${BUILD_DEPS} \
    && rm -rf /var/lib/apt/lists/*

RUN curl -L -o /tmp/antlr-3.4-complete.jar http://www.antlr3.org/download/antlr-3.4-complete.jar \
    && echo '#!/bin/bash' > /usr/local/bin/antlr3 \
    && echo 'exec java -cp /tmp/antlr-3.4-complete.jar org.antlr.Tool "$@"' >> /usr/local/bin/antlr3 \
    && chmod 775 /usr/local/bin/antlr3

RUN cd /tmp && \
    git clone https://github.com/owntone/owntone-server.git && \
    cd /tmp/owntone-server && \
    autoreconf -fi && \
    ./configure \
    --disable-spotify \
    --disable-lastfm \
    && \
    make && \
    make install DESTDIR=/tmp/owntone-install

FROM base AS runner
ARG BUILD_ARCH
COPY --from=builder /tmp/owntone-install /
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    ${RUN_DEPS} \
    && rm -rf /var/lib/apt/lists/*


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

RUN mkdir -p /var/log/nginx && ln -sf /dev/stdout /var/log/nginx/access.log && ln -sf /dev/stderr /var/log/nginx/error.log

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
