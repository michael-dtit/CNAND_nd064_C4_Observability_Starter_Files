import os
import requests
from flask import Flask, request
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

# Initialize Flask app
app = Flask(__name__)

# Set up OpenTelemetry
resource = Resource(attributes={
    "service.name": "sampleapp1"
})
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

# Configure OTLP exporter
otlp_exporter = OTLPSpanExporter(endpoint="http://jaeger-collector.observability.svc.cluster.local:4318")
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Instrument Flask and requests
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

@app.route("/")
def hello_world():
    return "Hello, World!\n\nThank you for visiting the site!\n\n"

@app.route("/api/second", methods=["GET", "POST"])
def jobs():
    print("Received request to /api/second")
    url = "http://second-sample-app.default.svc.cluster.local:8000"
    response = requests.get(url)
    return str(type(response))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888)
