FROM fedora:36

WORKDIR /tests

RUN mkdir -p /logs && \
    dnf makecache && \
    curl -fsSL https://get.docker.com | sh && \
    dnf install -y pip

COPY /requirements.txt /tests/
RUN pip install -r /tests/requirements.txt

COPY /commons/ /tests/commons/
RUN pip install /tests/commons/

COPY /test_* /tests/
COPY /conftest.py /tests/conftest.py
COPY /driver/scap.ko /driver/

ARG SINSP_TAG=latest
ENV SINSP_TAG=${SINSP_TAG}

ENTRYPOINT [ "pytest", "--html=/report/report.html" ]
