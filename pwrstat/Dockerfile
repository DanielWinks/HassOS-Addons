ARG BUILD_FROM
FROM ${BUILD_FROM}

ARG ARCH
ARG VERSION
COPY rootfs/*.deb /tmp/
COPY rootfs/pwrstat /

RUN apt-get update && apt-get dist-upgrade -y && \
    apt-get install -y procps curl && \
    chmod +x /init.sh && chmod +x /pwrstat_api.py && \
    pip install --trusted-host pypi.python.org -r requirements.txt && \
    apt-get -y --purge autoremove && apt-get clean && \
    rm -rf /tmp/* /var/tmp/* /var/lib/apt/lists/* && \
    if [[ "amd64" = *"$BUILD_ARCH"* ]]; \
        then \
            apt-get install -y /PPL-1.3.3-64bit.deb && \
            apt-get -y --purge autoremove && apt-get clean && \
            rm -rf /tmp/* /var/tmp/* /var/lib/apt/lists/* \
    fi && \
    if [[ "i386" = *"$BUILD_ARCH"* ]]; \
        then \
            apt-get install -y /PPL-1.3.3-32bit.deb && \
            apt-get -y --purge autoremove && apt-get clean && \
            rm -rf /tmp/* /var/tmp/* /var/lib/apt/lists/* \
    fi

RUN chmod +x /run.sh
CMD [ "/run.sh" ]