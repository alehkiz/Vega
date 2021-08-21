# syntax=docker/dockerfile:1

FROM python:3.9.5-slim-buster

WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update && apt-get install -y netcat

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip3 install -r requirements.txt
COPY ./sql/init.sql /docker-entrypoint-initdb.d/
COPY . /usr/src/app/
RUN apt-get -y install locales
# Set the locale
# RUN sed -i '/pt_BR.UTF-8/s/^# //g' /etc/locale.gen && \
#     locale-gen
ENV LANG pt_BR.UTF-8
ENV LANGUAGE pt_BR:pt
ENV LC_ALL pt_BR.UTF-8
# CMD [ "flask", "run", "--host=0.0.0.0"]
# run entrypoint.sh

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]