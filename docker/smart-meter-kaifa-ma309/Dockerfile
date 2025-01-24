FROM debian:latest

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dotenv \
    git \
    sudo \
    && apt-get clean

RUN sudo rm -rf /usr/lib/python3.11/EXTERNALLY-MANAGED

WORKDIR /app

RUN git clone https://github.com/M47784U3R/smart-meter-kaifa-MA309 /app

RUN mkdir -p logs

RUN pip install -r requirements/requirements.txt

CMD ["python3", "smart-meter.py"]