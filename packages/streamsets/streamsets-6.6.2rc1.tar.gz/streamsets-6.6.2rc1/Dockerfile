FROM python:3.8-slim
RUN apt-get update && \
    apt-get -y install \
    gcc \
    git \
    make
WORKDIR /root
ADD requirements.txt ./
RUN pip3 install -r requirements.txt
ADD . .
RUN make setup
RUN make build
