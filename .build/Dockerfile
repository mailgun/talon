FROM python:3.9-slim-buster AS deps

RUN apt-get update && \
    apt-get install -y build-essential git curl python3-dev libatlas3-base libatlas-base-dev liblapack-dev libxml2 libxml2-dev libffi6 libffi-dev musl-dev libxslt-dev

FROM deps AS testable
ARG REPORT_PATH

VOLUME ["/var/mailgun", "/etc/mailgun/ssl", ${REPORT_PATH}]

ADD . /app
WORKDIR /app
COPY wheel/* /wheel/

RUN mkdir -p ${REPORT_PATH}

RUN python ./setup.py build bdist_wheel -d /wheel && \
    pip install --no-deps /wheel/*

ENTRYPOINT ["/bin/sh", "/app/run_tests.sh"]
