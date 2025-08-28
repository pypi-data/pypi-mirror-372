# opentelemetry_config.py
import logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor

from django.apps import AppConfig

from fk_utils import SETTINGS

# Configurar logging solo si no está configurado
if not logging.getLogger().hasHandlers():
    logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def configure_tracer():
    try:
        trace.set_tracer_provider(
            TracerProvider(
                resource=Resource.create({"service.name": SETTINGS.OTLP_NAME})
            )
        )
        otlp_exporter = OTLPSpanExporter(
            endpoint=f"{SETTINGS.OTLP_HOST}:{SETTINGS.OTLP_PORT}", insecure=True
        )
        trace.get_tracer_provider().add_span_processor(
            BatchSpanProcessor(otlp_exporter)
        )
        logger.info("OpenTelemetry tracer configurado correctamente.")
    except Exception as e:
        logger.error(f"Error al configurar OpenTelemetry: {e}")


def instrument_app():
    instrumentors = [
        DjangoInstrumentor(),
        RequestsInstrumentor(),
        Psycopg2Instrumentor(),
    ]
    try:
        for instrumentor in instrumentors:
            instrumentor.instrument()
        logger.info("Aplicación instrumentada correctamente con OpenTelemetry.")
    except Exception as e:
        logger.error(f"Error al instrumentar la aplicación: {e}")


class OpenTelemetryConfig(AppConfig):
    name = "fk_utils.traces.opentelemetry.django.trace"
    verbose_name = "OpenTelemetry Integration"

    def ready(self):
        configure_tracer()
        instrument_app()
