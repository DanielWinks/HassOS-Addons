ARG BUILD_FROM

FROM scratch as dl_cacher

ADD https://github.com/merbanan/rtl_433/archive/21.05.tar.gz /rtl_433.tar.gz
ADD https://github.com/osmocom/rtl-sdr/archive/0.6.0.tar.gz /rtl_sdr.tar.gz

FROM alpine:3.13 as builder

ENV LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/lib64:/usr/local/lib"

RUN apk add --no-cache --update cmake build-base libusb-dev bash

COPY --from=dl_cacher / /tmp

RUN mkdir -p /build/rtl_433 /build/rtl_sdr && \
    tar -zxvf /tmp/rtl_433.tar.gz -C /build/rtl_433 --strip-components=1 && \
    tar -zxvf /tmp/rtl_sdr.tar.gz -C /build/rtl_sdr --strip-components=1

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

RUN apk add --no-cache --update libusb

COPY --from=builder /usr/local/ /usr/local/
COPY --from=builder /etc/modprobe.d/blacklist-dvb_usb_rtl28xxu.conf /etc/modprobe.d/blacklist-dvb_usb_rtl28xxu.conf
COPY --from=builder /etc/udev/rules.d/rtl-sdr.rules /etc/udev/rules.d/rtl-sdr.rules

COPY rootfs /

RUN chmod +x /run.sh
CMD [ "/run.sh" ]