FROM python:3.13-slim as BUILD

WORKDIR /temp

RUN pip install uv

COPY ./pyproject.toml /temp/pyproject.toml
COPY ./uv.lock /temp/uv.lock

RUN uv export --format requirements.txt -o requirements.txt --no-cache

FROM python:3.13-slim 

ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /usr/backend

COPY --from=BUILD /temp/requirements.txt /usr/backend/requirements.txt

RUN pip install --no-cache-dir -r /usr/backend/requirements.txt

COPY . /usr/backend