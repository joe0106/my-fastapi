FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE 1
WORKDIR /usr/backend
COPY ./requirements.txt /usr/backend/requirements.txt
RUN pip install --no-cache-dir -r /usr/backend/requirements.txt
COPY . /usr/backend