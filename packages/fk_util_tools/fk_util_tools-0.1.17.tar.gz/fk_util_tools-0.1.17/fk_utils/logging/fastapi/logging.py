import logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

from fk_utils import SETTINGS

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def configure_tracer():
    try:
        # Configurar el proveedor de trazas
        trace.set_tracer_provider(TracerProvider(
            resource=Resource.create({"service.name": SETTINGS.OTLP_NAME})
        ))

        # Configurar el exportador OTLP
        otlp_exporter = OTLPSpanExporter(
            endpoint=f"{SETTINGS.OTLP_HOST}:{SETTINGS.OTLP_PORT}",
            insecure=True
        )

        # Añadir el procesador de spans
        trace.get_tracer_provider().add_span_processor(
            BatchSpanProcessor(otlp_exporter)
        )

        logger.info("OpenTelemetry tracer configurado correctamente.")

    except Exception as e:
        logger.error(f"Error al configurar el tracer de OpenTelemetry: {e}")


def instrument_app(app):
    try:
        # Instrumentar FastAPI
        FastAPIInstrumentor.instrument_app(app)

        # Instrumentar SQLAlchemy
        SQLAlchemyInstrumentor().instrument()

        # Instrumentar Requests
        RequestsInstrumentor().instrument()

        logger.info("Aplicación instrumentada correctamente con OpenTelemetry.")

    except Exception as e:
        logger.error(f"Error al instrumentar la aplicación: {e}")
