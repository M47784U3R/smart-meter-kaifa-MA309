FROM python:3

RUN git clone https://github.com/M47784U3R/smart-meter-kaifa-MA309

RUN pip3 install -r /smart-meter-kaifa-MA309/requirements/requirements.txt

# expose port
EXPOSE 5000