FROM ubuntu:18.04
LABEL maintainer "Slava Sukhoy <dreasty.d@gmail.com>"
RUN apt-get update
RUN mkdir /webapp
WORKDIR /webapp
COPY . /webapp
RUN apt install -y python3.6 python3-pip
RUN pip3 install --no-cache-dir -r requirements.txt
EXPOSE 5000
CMD python3 webapp.py