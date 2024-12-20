# start from base
FROM debian

# install system-wide deps for python
RUN apt-get update -yqq
RUN apt-get install -yqq python3-pip python3-dev curl gnupg git

RUN git clone https://github.com/M47784U3R/smart-meter-kaifa-MA309

RUN pip3 install -r requirements/requirements.txt

# expose port
EXPOSE 5000