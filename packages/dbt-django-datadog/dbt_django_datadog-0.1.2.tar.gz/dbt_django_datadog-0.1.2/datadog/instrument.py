import os

from django.conf import settings
import ddtrace


def _instrument():
    # this applies datadog
    import ddtrace.auto


def configure_datadog():
    """Instrument the app for Datadog applying the default DBT config"""
    config = ddtrace.config

    service_name = os.environ.get("COPILOT_SERVICE_NAME", "undefined")
    application_name = os.environ.get("COPILOT_APPLICATION_NAME", "undefined")
    environment_name = os.environ.get("COPILOT_ENVIRONMENT_NAME", "undefined")

    # consistent serivce name, not relying on configuration in manifest.yml
    datadog_service_name = f"{application_name}-{service_name}"
    config.django["service_name"] = datadog_service_name

    # No clean way to set these settings as per the ddtrace/Django docs, we'll use `os.environ`
    os.environ.setdefault("DD_ENV", environment_name)
    os.environ.setdefault(
        "DD_SERVICE_MAPPING",
        f"aws.s3:{application_name}-web-aws.s3,elasticsearch:{application_name}-web-elasticsearch,nginx:{application_name}-web-nginx,ipfilter:{application_name}-web-ipfilter,opensearch:{application_name}-web-opensearch,postgres:{application_name}-web-postgres,redis:{application_name}-web-redis,requests:{application_name}-web",
    )
    os.environ.setdefault("DD_LOGS_INJECTION", "true")
    os.environ.setdefault("DD_RUNTIME_METRICS_ENABLED", "true")
    os.environ.setdefault("DD_PROFILING_TIMELINE_ENABLED", "true")
    os.environ.setdefault("DD_PROFILING_ENABLED", "true")
    os.environ.setdefault(
        "DD_TRACE_HEADER_TAGS",
        "User-Agent:http.user_agent,Referer:http.referer,Content-Type:http.content_type,Etag:http.etag",
    )

    # additional options that can only be configured this way - they're not availble if we use ddtrace-run
    config.django["trace_fetch_methods"] = True  # include the method names
    config.django["trace_query_string"] = True  # include the trace query string

    database_name = getattr(settings, "DATABASES", {}).get("default", {}).get("NAME")
    if database_name:
        config.django["database_service_name"] = database_name

    _instrument()
