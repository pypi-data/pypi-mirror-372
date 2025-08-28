import logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.botocore import BotocoreInstrumentor
from opentelemetry.instrumentation.aws_lambda import AwsLambdaInstrumentor

from fk_utils import SETTINGS

# Configurar logging solo si no está configurado
if not logging.getLogger().hasHandlers():
    logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def configure_tracer():
    try:
        tracer_provider = TracerProvider(
            resource=Resource.create({"service.name": SETTINGS.OTLP_NAME})
        )
        trace.set_tracer_provider(tracer_provider)
        otlp_exporter = OTLPSpanExporter(
            endpoint=f"{SETTINGS.OTLP_HOST}:{SETTINGS.OTLP_PORT}",
            insecure=True
        )
        tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
        logger.error("OpenTelemetry tracer configurado correctamente.")
    except Exception as e:
        logger.error(f"Error al configurar OpenTelemetry: {e}")


def instrument_app(app):
    instrumentors = [
        (FastAPIInstrumentor(), {"app": app}),
        (SQLAlchemyInstrumentor(), {}),
        (RequestsInstrumentor(), {}),
        (BotocoreInstrumentor(), {}),
        (AwsLambdaInstrumentor(), {})
    ]
    try:
        configure_tracer()
        for instrumentor, kwargs in instrumentors:
            if 'app' in kwargs:
                instrumentor.instrument_app(kwargs['app'])
            else:
                instrumentor.instrument()
        logger.error("Aplicación instrumentada correctamente con OpenTelemetry.")
    except Exception as e:
        logger.error(f"Error al instrumentar la aplicación: {e}")


