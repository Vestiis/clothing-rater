FROM python:3.8.10-slim

# install python packages
COPY setup.py .
RUN pip install --upgrade pip
RUN pip install -e .

# add code
COPY . .

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

CMD exec uvicorn src.app.api:app --host 0.0.0.0 --port 8080 --log-level info --reload
