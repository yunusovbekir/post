FROM python:3.8.18-alpine

ENV PYTHONUNBUFFERED 1

COPY .env .env
COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache linux-headers
RUN apk add --update --no-cache postgresql-client jpeg-dev
RUN apk add --no-cache libressl-dev musl-dev libffi-dev
RUN apk add --update --no-cache --virtual .tmp-build-deps \
      python3-dev gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev
RUN pip install -r /requirements.txt
RUN apk del .tmp-build-deps
RUN apk del libressl-dev musl-dev libffi-dev

RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN adduser -D user
RUN chown -R user:user /app/
RUN chmod -R 777 /app/
USER user
