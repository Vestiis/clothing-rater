FROM python:3.8.10-slim

ARG ssh_prv_key
ARG ssh_pub_key

RUN apt-get update && \
    apt-get install -y \
    git \
    openssh-server && \
    apt-get dist-upgrade -y libmagic1

# Authorize SSH Host
RUN mkdir -p /root/.ssh && \
    chmod 0700 /root/.ssh && \
    ssh-keyscan github.com > /root/.ssh/known_hosts

# Add the keys and set permissions
RUN echo "$ssh_prv_key" > /root/.ssh/id_rsa && \
    echo "$ssh_pub_key" > /root/.ssh/id_rsa.pub && \
    chmod 600 /root/.ssh/id_rsa && \
    chmod 600 /root/.ssh/id_rsa.pub

# install python packages
COPY setup.py .
RUN pip install --upgrade pip
RUN pip install -e .

# add code
COPY . .

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

CMD exec uvicorn src.app.api:app --host 0.0.0.0 --port 8080 --log-level info --reload
