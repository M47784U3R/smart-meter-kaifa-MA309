FROM debian:latest

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    sudo \
    && apt-get clean

RUN sudo rm -rf /usr/lib/python3.11/EXTERNALLY-MANAGED

WORKDIR /app

RUN git clone https://github.com/M47784U3R/smart-meter-kaifa-MA309 /app

RUN mkdir -p /app/logs

RUN pip3 install -r /app/requirements/requirements.txt

CMD ["python3", "smart-meter.py"]