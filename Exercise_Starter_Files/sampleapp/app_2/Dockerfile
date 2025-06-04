FROM python:3.12

RUN pip install flask requests \
        opentelemetry-api opentelemetry-sdk \
        opentelemetry-exporter-otlp \
        opentelemetry-instrumentation-flask \
        opentelemetry-instrumentation-requests
          
COPY . /usr/src/myapp

ENV FLASK_APP app.py

WORKDIR /usr/src/myapp

CMD flask run --host=0.0.0.0 --port=8000
