"""Integraciones opcionales: cada una se activa solo si su variable de entorno tiene valor."""

import logging

from fastapi import FastAPI

from app.config import Settings

logger = logging.getLogger(__name__)


def init_otel(app: FastAPI, settings: Settings) -> bool:
    """Instrumenta la app con OpenTelemetry si `OTEL_EXPORTER_OTLP_ENDPOINT` tiene valor.

    Los imports son locales para no pagar su costo cuando la integración está apagada.
    Devuelve True si quedó activa.
    """
    if not settings.otel_exporter_otlp_endpoint:
        return False
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    endpoint = settings.otel_exporter_otlp_endpoint.rstrip("/") + "/v1/traces"
    provider = TracerProvider(
        resource=Resource.create({"service.name": settings.otel_service_name})
    )
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint)))
    FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)
    logger.info("opentelemetry activado", extra={"otel_endpoint": endpoint})
    return True
