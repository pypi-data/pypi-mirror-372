# Datadog for DBTP hosted Django applications

Auto instrument Django applications running in DBTP (AWS Copilot/Fargate).

For more information see: https://ddtrace.readthedocs.io/en/stable/integrations.html#django

## Prerequisits

Your service needs the Datadog agent sidecar. See: https://platform.readme.trade.gov.uk/next-steps/observability/datadog/enable-datadog-for-your-application/

## Setup

1. Install: `pip install dbt-django-datadog`

2. Add `datadog` to settings.INSTALLED_APPS

3. Add `datadog.middleware.DatadogMiddleware` to settings.MIDDLEWARE

## Configuration

The module applies a default configuration, which means that you don't need to add any custom environment variables to your service's config (note: the Datadog agent needs its own environment variables). However, if you do set Datadog environent variables in your service's `manifest.yml` file, then they will override the default configuration.

_Example:_

Profiling is enabled by default. You can disable profiling by setting the `DD_PROFILING_ENABLED` to `false`.

## Default settings

| Environment variable | Default setting |
| -------------------- | --------------- |
| DD_ENV | "${COPILOT_ENVIRONMENT_NAME}" |
| DD_SERVICE | "${COPILOT_APPLICATION_NAME}-${COPILOT_SERVICE_NAME}" |
| DD_SERVICE_MAPPING | "aws.s3:${COPILOT_APPLICATION_NAME}-web-aws.s3,elasticsearch:${COPILOT_APPLICATION_NAME}-web-elasticsearch,nginx:${COPILOT_APPLICATION_NAME}-web-nginx,ipfilter:${COPILOT_APPLICATION_NAME}-web-ipfilter,opensearch:${COPILOT_APPLICATION_NAME}-web-opensearch,postgres:${COPILOT_APPLICATION_NAME}-web-postgres,redis:${COPILOT_APPLICATION_NAME}-web-redis,requests:${COPILOT_APPLICATION_NAME}-web" |
| DD_LOGS_INJECTION | true |
| DD_RUNTIME_METRICS_ENABLED | true |
| DD_PROFILING_TIMELINE_ENABLED | true |
| DD_PROFILING_ENABLED | true |
| DD_TRACE_HEADER_TAGS | "User-Agent:http.user_agent,Referer:http.referer,Content-Type:http.content_type,Etag:http.etag" |

## Contributing

If you would like to contribute, raise a pull request and ask the SRE team for a code review.
