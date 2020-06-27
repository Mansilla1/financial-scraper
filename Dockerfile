FROM python:3.8.3

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt
RUN python manage.py migrate
