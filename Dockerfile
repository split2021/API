
FROM python:3.9

ENV PYTHONUNBUFFERED 1

RUN mkdir /api
WORKDIR /api

ADD requirements.txt /api
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ADD . /api/

EXPOSE 8080 80 443
