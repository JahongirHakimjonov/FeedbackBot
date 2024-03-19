FROM python:3.10-slim-buster

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY ./compose/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY ./compose/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

COPY ./check_errors.sh /check_errors.sh
RUN chmod +x /check_errors.sh

COPY ./autorun.sh /autorun.sh
RUN chmod +x /autorun.sh

WORKDIR /app

ENTRYPOINT ["/entrypoint"]