ARG BUILD_FROM

FROM ${BUILD_FROM} as buildstage
ARG BUILD_ARCH

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

ARG DAAPD_RELEASE
ARG LIBSPOTIFY_VERSION=12.1.51

RUN \
    apk add --no-cache \
    alsa-lib-dev \
    autoconf \
    automake \
    avahi-dev \
    bash \
    bsd-compat-headers \
    confuse-dev \
    curl \
    curl-dev \
    ffmpeg-dev \
    file \
    flac-dev \
    g++ \
    gcc \
    gettext-dev \
    gnutls-dev \
    gperf \
    json-c-dev \
    libcurl \
    libevent-dev \
    libgcrypt-dev \
    libogg-dev \
    libplist-dev \
    libressl-dev \
    libsodium-dev \
    libtool \
    libunistring-dev \
    libwebsockets-dev \
    make \
    openjdk8-jre-base \
    protobuf-c-dev \
    sqlite-dev \
    taglib-dev \
    tar && \
    apk add --no-cache \
    --repository=http://dl-cdn.alpinelinux.org/alpine/edge/community \
    mxml-dev

RUN \
    mkdir -p \
    /tmp/source/owntone && \
    echo \
    "#!/bin/bash" > /tmp/source/antlr3 && \
    echo \
    "exec java -cp /tmp/source/antlr-3.4-complete.jar org.antlr.Tool \"\$@\"" >> /tmp/source/antlr3 && \
    chmod a+x /tmp/source/antlr3 && \
    curl -o \
    /tmp/source/antlr-3.4-complete.jar -L \
    http://www.antlr3.org/download/antlr-3.4-complete.jar

RUN \
    curl -o \
    /tmp/libantlr3c-3.4.tar.gz -L \
    https://github.com/antlr/website-antlr3/raw/gh-pages/download/C/libantlr3c-3.4.tar.gz && \
    tar xf /tmp/libantlr3c-3.4.tar.gz  -C /tmp && \
    cd /tmp/libantlr3c-3.4 && \
    if [[ "${BUILD_ARCH}" = "amd64" ]]; \
    then ./configure \
    --enable-64bit \
    --prefix=/usr; && \
    fi && \
    if [[ "${BUILD_ARCH}" = "i386" ]]; \
    then ./configure \
    --prefix=/usr; && \
    fi && \
    if [[ "${BUILD_ARCH}" = "aarch64" ]]; \
    then ./configure \
    --build arm-unknown-linux-gnueabi \
    --disable-abiflags \
    --disable-antlrdebug \
    --enable-64bit \
    --prefix=/usr; && \
    fi && \
    if [[ "${BUILD_ARCH}" = "armv7" ]]; \
    then ./configure \
    --build arm-unknown-linux-gnueabihf \
    --disable-abiflags \
    --disable-antlrdebug \
    --prefix=/usr; && \
    fi && \
    make && \
    make DESTDIR=/tmp/antlr3c-build install && \
    export LDFLAGS="-L/tmp/antlr3c-build/usr/lib" && \
    export CFLAGS="-I/tmp/antlr3c-build/usr/include"

RUN \
    if [ -z ${DAAPD_RELEASE+x} ]; then \
    DAAPD_RELEASE=$(curl -sX GET "https://api.github.com/repos/owntone/owntone-server/releases/latest" \
    | awk '/tag_name/{print $4;exit}' FS='[""]'); \
    fi && \
    curl -L https://github.com/mopidy/libspotify-archive/blob/master/libspotify-${LIBSPOTIFY_VERSION}-Linux-${BUILD_ARCH}-release.tar.gz?raw=true | tar -xzf- -C /tmp/source/ && \
    mv /tmp/source/libspotify* /tmp/source/libspotify && \
    sed -i 's/ldconfig//' /tmp/source/libspotify/Makefile && \
    make -C /tmp/source/libspotify prefix=/tmp/libspotify-build install && \
    rm -rf /tmp/source/libspotify && \
    export LIBSPOTIFY_CFLAGS="-I/tmp/libspotify-build/include" && \
    export LIBSPOTIFY_LIBS="/tmp/libspotify-build/lib/libspotify.so" && \
    curl -o \
    /tmp/source/owntone.tar.gz -L \
    "https://github.com/owntone/owntone-server/archive/${DAAPD_RELEASE}.tar.gz" && \
    tar xf /tmp/source/owntone.tar.gz -C \
    /tmp/source/owntone --strip-components=1 && \
    export PATH="/tmp/source:$PATH"

RUN \
    cd /tmp/source/owntone && \
    autoreconf -i -v && \
    ./configure \
    --build=$CBUILD \
    --enable-chromecast \
    --enable-itunes \
    --enable-lastfm \
    --enable-mpd \
    --enable-spotify \
    --host=$CHOST \
    --infodir=/usr/share/info \
    --localstatedir=/var \
    --mandir=/usr/share/man \
    --prefix=/usr \
    --sysconfdir=/etc && \
    make && \
    make DESTDIR=/tmp/daapd-build install


FROM ${BUILD_FROM}

COPY --from=buildstage /tmp/daapd-build/ /
COPY --from=buildstage /tmp/antlr3c-build/ /
COPY --from=buildstage /tmp/libspotify-build/ /

ARG BUILD_ARCH
RUN \
    apk add --no-cache \
    avahi \
    confuse \
    dbus \
    ffmpeg \
    json-c \
    libcurl \
    libevent \
    libgcrypt \
    libplist \
    libressl \
    libsodium \
    libunistring \
    libwebsockets \
    protobuf-c \
    sqlite \
    sqlite-libs && \
    apk add --no-cache \
    --repository=http://dl-cdn.alpinelinux.org/alpine/edge/community \
    mxml


RUN cd /etc \
    && sed -i -e 's/\(uid.*=.*\)/uid = "root"/g' owntone.conf.orig \
    && sed -i s#"ipv6 = yes"#"ipv6 = no"#g owntone.conf.orig \
    && sed -i s#/srv/music#/config/owntone/music#g owntone.conf.orig \
    && sed -i s#/usr/local/var/cache/owntone/songs3.db#/config/owntone/cache/songs3.db#g owntone.conf.orig \
    && sed -i s#/usr/local/var/cache/owntone/cache.db#/config/owntone/cache/cache.db#g owntone.conf.orig \
    && sed -i s#/usr/local/var/log/owntone.log#/dev/stdout#g owntone.conf.orig \
    && sed -i "/websocket_port\ =/ s/# *//" owntone.conf.orig \
    && sed -i "/trusted_networks\ =/ s/# *//" owntone.conf.orig \
    && sed -i "/pipe_autostart\ =/ s/# *//" owntone.conf.orig \
    && sed -i "/db_path\ =/ s/# *//" owntone.conf.orig \
    && sed -i "/cache_path\ =/ s/# *//" owntone.conf.orig

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
