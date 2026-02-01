import os
import requests
from flask import Flask, request
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

app = Flask(__name__)

# Instrument Flask and requests
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

# Define the resource with service name
resource = Resource(attributes={
    "service.name": "sampleapp2"
})

# Set up the tracer provider and add the OTLP exporter
provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://jaeger-collector.observability.svc.cluster.local:4318"))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

@app.route("/")
def homepage():
    gh_jobs = "https://www.github.careers/api/jobs?keywords=python"

    with tracer.start_as_current_span("get-python-jobs") as span:
        span.set_attribute("http.url", gh_jobs)
        res = requests.get(gh_jobs)
        span.set_attribute("http.status_code", res.status_code)

    with tracer.start_as_current_span("get-json") as span:
        myjson = res.json()['jobs']
        span.set_attribute("python_jobs", len(myjson))
        pull_python_jobs = map(lambda item: item['data']["title"], myjson)

    return "Tracing Results: " + ", ".join(pull_python_jobs)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
