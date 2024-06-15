FROM python:3.9-slim-buster

RUN apt-get update && apt-get -y install cron

WORKDIR /app
COPY ./app /app
COPY ./requirements.txt /app/

RUN pip3 install -r requirements.txt

RUN chmod +x /app/downlatestimg.sh

# CRONJOB
RUN touch /var/log/cron.log
COPY ./app/crontab /etc/cron.d/crontab
RUN chmod 0644 /etc/cron.d/crontab
RUN crontab /etc/cron.d/crontab
CMD cron && tail -f /var/log/cron.log