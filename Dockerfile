FROM python:alpine
# using python 3.10

LABEL maintainer="art.goldhammer@gmail.com"



# substituting gunicorn for uwsgi
RUN apk update &&\
    apk upgrade &&\
    apk add --no-cache logrotate  supervisor

RUN pip install --no-cache-dir --upgrade pip==22.0.4 setuptools wheel

RUN mkdir /nooze2; mkdir -p /var/log/nooze2
RUN touch /var/log/nooze2/nooze2.log

RUN mkdir -p /var/log/gunicorn
RUN touch /var/log/gunicorn/gunicorn.log
RUN mkdir /app

RUN chmod 755 /var/log/gunicorn
RUN chmod 755 /var/log/nooze2

# install the standing requirements
COPY requirements.txt /nooze2
RUN pip install --no-cache-dir -r /nooze2/requirements.txt
RUN pip install --no-cache-dir gunicorn==20.1.0

# install the app environment
COPY nzdb/ /nooze/nzdb/
COPY setup.py /nooze2
WORKDIR /nooze2
# leave installation editable for now
RUN pip install --no-cache-dir .
RUN rm -rf /nooze2
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

