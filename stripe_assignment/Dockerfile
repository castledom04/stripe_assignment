FROM python:3.8-slim-buster

WORKDIR /home/stripe_assignment/django

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install -qy \
    build-essential \
    gdal-bin \
    gettext \
    libpq-dev \
    libgeos-dev \
    libgdal-dev \
    libbz2-dev \
    libffi-dev \
    libjson-c3 \
    libjson-c-dev \
    libjpeg-dev \
    libxml2-dev \
    libxslt1-dev \
    python-psycopg2 \
    python3-dev \
    # Needed for entrypoint_development.sh
    netcat

RUN pip install --upgrade pip
COPY ./requirements.txt /home/stripe_assignment/django/requirements.txt
RUN pip install -r requirements.txt

COPY . /home/stripe_assignment/django/

ENTRYPOINT ["/home/stripe_assignment/django/entrypoint_development.sh"]
