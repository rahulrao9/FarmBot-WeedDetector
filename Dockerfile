FROM ubuntu:20.04

# Set the timezone to Kolkata
ENV TZ=Asia/Kolkata
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update && \
    apt-get install -y \
    dos2unix \
    python3 \
    python3-pip \
    cron \ 
    curl \
    jq

WORKDIR /app

COPY ./app /app
COPY ./requirements.txt /app/

RUN pip3 install -r requirements.txt

RUN dos2unix /app/*.sh

RUN chmod +x /app/*.sh
RUN chmod +x /app/driveUploader.py
RUN chmod +x /app/main.py

RUN touch /var/log/cron.log
COPY ./app/crontab /etc/cron.d/crontab
RUN chmod 0644 /etc/cron.d/crontab
RUN crontab /etc/cron.d/crontab

CMD cron && tail -f /var/log/cron.log