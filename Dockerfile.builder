FROM fedora:36

RUN dnf install -y \
    gcc \
    gcc-c++ \
    libasan \
    git \
    make \
    cmake \
    autoconf \
    automake \
    pkg-config \
    patch \
    ncurses-devel \
    libtool \
    elfutils-libelf-devel \
    diffutils \
    which \
    perl-core \
    clang \
    kmod \
# Dependencies needed to build falcosecurity/libs.
    libb64-devel \
    c-ares-devel \
    libcurl \
    libcurl-devel \
    grpc-cpp \
    grpc-devel \
    grpc-plugins \
    jq-devel \
    jsoncpp-devel \
    openssl-devel \
    tbb-devel \
    zlib-devel

ENTRYPOINT ["bash", "-c"]
