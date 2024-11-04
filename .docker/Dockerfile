FROM python:3.12

COPY . /app
WORKDIR /app

RUN apt-get update
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN echo "alias dev='python /app/dev.py'" >> ~/.bashrc
