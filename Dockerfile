FROM golang:1.14-buster

COPY entrypoint.py /entrypoint.py
RUN apt-get update && apt-get install -y python-pip
RUN pip install requests

ENTRYPOINT ["/entrypoint.py"]
