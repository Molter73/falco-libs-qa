FROM fedora:36

RUN dnf install -y \
    libcurl \
    grpc-cpp \
    grpc \
    grpc-plugins \
    jq \
    jsoncpp \
    openssl \
    libasan \
    tbb

COPY /userspace/sinsp-example /usr/local/bin/sinsp-example
COPY /driver/probe.o /driver/probe.o

ENTRYPOINT [ "sinsp-example", "-j" ]
