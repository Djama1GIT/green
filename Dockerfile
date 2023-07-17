FROM python:3.11

RUN mkdir /app

WORKDIR /app

RUN apt-get update

RUN apt-get install -y npm

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

