# syntax=docker/dockerfile:1
FROM pypy
COPY . /app
RUN ln -sf /usr/share/zoneinfo/Europe/Berlin /etc/localtime
RUN cd /app/ && CRYPTOGRAPHY_DONT_BUILD_RUST=1 pip install -r requirements.txt
CMD python /app/bot.py