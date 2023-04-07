FROM python:3.10-buster

RUN apt-get update && \
    apt-get install -y \
        libpq-dev \
        curl \
        nano && \
    rm -rf /var/lib/apt/lists/*

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3.10 get-pip.py && \
    rm get-pip.py


ADD ./src/server/requirements.txt source/requirements.txt
RUN pip install -r /source/requirements.txt

COPY ./bin/start_server.py /source/run.py
COPY ./src/share /source/share
COPY ./src/server /source/server
COPY ./VERSION source/VERSION

ENV PYTHONPATH /source/

WORKDIR /source/

CMD ["python3.10", "run.py"]
