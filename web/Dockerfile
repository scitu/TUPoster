FROM python:3.6

RUN mkdir /web
WORKDIR /web
ADD ./requirements.txt /web/requirements.txt
RUN pip install -r requirements.txt
ADD . /web
