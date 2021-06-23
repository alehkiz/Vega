# syntax=docker/dockerfile:1

FROM python:3.9.5-slim-buster

WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update && apt-get install -y netcat

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
# CMD [ "flask", "run", "--host=0.0.0.0"]
# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]