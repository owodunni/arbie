FROM python:3.8-slim

# Install OpenJDK-8
RUN mkdir /usr/share/man/man1 && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive \
    apt-get -y --no-install-recommends install build-essential \
    default-jdk-headless && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /arbie

ADD gradlew gradlew
ADD gradle gradle

RUN ./gradlew

ADD pip pip
RUN pip install -r pip/requirements.txt
RUN pip install -r pip/requirements-dev.txt
