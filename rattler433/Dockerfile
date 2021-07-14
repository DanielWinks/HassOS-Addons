ARG BUILD_FROM

FROM alpine:3.13 as builder

RUN apk add --no-cache --update cmake build-base libusb-dev bash curl

ARG RTL_433_VER
ARG RTL_SDR_VER
RUN curl -Lso /tmp/rtl_433.tar.gz \
    "https://github.com/merbanan/rtl_433/archive/${RTL_433_VER}.tar.gz"
RUN curl -Lso /tmp/rtl_sdr.tar.gz \
    "https://github.com/osmocom/rtl-sdr/archive/${RTL_SDR_VER}.tar.gz"

ENV LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/lib64:/usr/local/lib"

RUN mkdir -p /build/rtl_433 /build/rtl_sdr && \
    tar -zxf /tmp/rtl_433.tar.gz -C /build/rtl_433 --strip-components=1 && \
    tar -zxf /tmp/rtl_sdr.tar.gz -C /build/rtl_sdr --strip-components=1

RUN mkdir /build/rtl_sdr/out && cd /build/rtl_sdr/out && \
    cmake ../ -DINSTALL_UDEV_RULES=ON -DDETACH_KERNEL_DRIVER=ON && \
    make  && \
    make install

RUN mkdir /build/rtl_433/out && cd /build/rtl_433/out && \
    cmake ../ && \
    make && \
    make install

RUN echo 'blacklist dvb_usb_rtl28xxu' > /etc/modprobe.d/blacklist-dvb_usb_rtl28xxu.conf

FROM ${BUILD_FROM}

ENV RTL_OPTS=""
ENV LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/lib64:/usr/local/lib"

WORKDIR /

RUN apk add --no-cache --update libusb python3 py3-pip && \
    python3 -m pip install paho-mqtt ruamel.yaml

COPY --from=builder /usr/local/ /usr/local/
COPY --from=builder /etc/modprobe.d/blacklist-dvb_usb_rtl28xxu.conf /etc/modprobe.d/blacklist-dvb_usb_rtl28xxu.conf
COPY --from=builder /etc/udev/rules.d/rtl-sdr.rules /etc/udev/rules.d/rtl-sdr.rules

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