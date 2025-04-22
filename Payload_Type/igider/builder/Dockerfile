FROM mythic_payload_builder:latest

RUN apt-get update && \
    apt-get install -y python3-pip build-essential curl && \
    pip3 install pyinstaller cryptography requests pyOpenSSL &&\
    apt-get install -y upx
WORKDIR /builder