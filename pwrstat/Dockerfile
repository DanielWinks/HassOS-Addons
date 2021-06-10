ARG BUILD_FROM
FROM ${BUILD_FROM}

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

ARG BUILD_ARCH
ARG VERSION
COPY rootfs /

RUN set -x && apt-get update && apt-get dist-upgrade -y && \
    apt-get install -y procps curl && \
    echo "deb http://http.us.debian.org/debian/ \
    testing non-free contrib main" >> \
    /etc/apt/sources.list.d/testing.list && \
    apt-get update && \
    apt-get install -y python3 python3-pip && \
    pip3 install --trusted-host pypi.python.org -r /pwrstat/requirements.txt && \
    if [[ "${BUILD_ARCH}" = "amd64" ]]; \
        then apt-get install -y /PPL-1.3.3-64bit.deb; \
    fi && \
    if [[ "${BUILD_ARCH}" = "i386" ]]; \
        then apt-get install -y /PPL-1.3.3-32bit.deb; \
    fi && \
    apt-get -y --purge autoremove && apt-get clean && \
    rm -rf /tmp/* /var/tmp/* /var/lib/apt/lists/* \
        /PPL-1.3.3-64bit.deb /PPL-1.3.3-32bit.deb


RUN chmod +x /run.sh /pwrstat/pwrstat_api.py
CMD [ "/run.sh" ]