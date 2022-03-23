FROM python:alpine
# using python 3.10

LABEL maintainer="art.goldhammer@gmail.com"

# substituting gunicorn for uwsgi
RUN apk add --update --no-cache \
    # uwsgi-python3 \
    logrotate \
    supervisor

RUN pip install --no-cache-dir --upgrade pip==22.0.3

RUN mkdir /nooze; mkdir -p /var/log/nooze
RUN touch /var/log/nooze/nooze.log

RUN mkdir -p /var/log/gunicorn
RUN touch /var/log/gunicorn/gunicorn.log
RUN mkdir /app

RUN mkdir -p /var/log/uwsgi
RUN touch /var/log/uwsgi/uwsgi.log

RUN chmod 755 /var/log/gunicorn
RUN chmod 755 /var/log/nooze
RUN chmod 755 /var/log/uwsgi

# install the standing requirements
COPY requirements.txt /nooze
RUN pip install --no-cache-dir -r /nooze/requirements.txt
RUN pip install --no-cache-dir gunicorn==20.1.0

# install the app environment
COPY nzdb/ /nooze/nzdb/
COPY setup.py /nooze
WORKDIR /nooze
# leave installation editable for now
RUN pip install --no-cache-dir -e .
# RUN rm -rf /nooze
# 
# CMD tail -f /dev/null
COPY app/ /app/
WORKDIR /app
RUN cp /app/logging/*conf /etc/logrotate.d
RUN chmod 644 /etc/logrotate.d/*.conf

# the following line is necessary to make logrotate run w/o hiccup
RUN touch /var/log/messages
#
# ENTRYPOINT ["supervisord", "-n"]

