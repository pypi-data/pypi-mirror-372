import json
from urllib.parse import urlparse
from asgiref.sync import iscoroutinefunction, sync_to_async
import ddtrace
from ddtrace import tracer
from ddtrace.ext import http, user as dd_user
from django.conf import settings


def sanitise_data(data):
    sensitive_keys = {"password", "secret", "token", "api_key", "credit_card"}
    if isinstance(data, dict):
        return {
            k: "***" if k.lower() in sensitive_keys else sanitise_data(v)
            for k, v in data.items()
        }
    elif isinstance(data, list):
        return [sanitise_data(item) for item in data]
    return data


def truncate_body(body, max_length=1024):
    if len(body) > max_length:
        return body[:max_length] + "... [truncated]"
    return body


class DatadogMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        self.is_async = iscoroutinefunction(self.get_response)

    def _sync_process_request(self, request):
        span = tracer.current_root_span()
        # span = tracer.current_span()
        if not span:
            span = tracer.trace("django.datadog")

        # span.set_tag(http.METHOD, request.method)
        # span.set_tag(http.URL, request.build_absolute_uri())

        # parsed_url = urlparse(request.build_absolute_uri())
        # span.set_tag("http.query_string", parsed_url.query)

        cookies = {k: v for k, v in request.COOKIES.items()}
        sanitised_cookies = sanitise_data(cookies)
        span.set_tag("http.cookies", json.dumps(sanitised_cookies, default=str))

        if request.method in ("POST", "PUT", "PATCH") and request.body:
            try:
                content_type = request.content_type.lower()
                if "json" in content_type:
                    body_data = json.loads(request.body)
                    sanitised_body = sanitise_data(body_data)
                    body_str = json.dumps(sanitised_body)
                elif "form" in content_type:
                    body_data = request.POST.dict()
                    sanitised_body = sanitise_data(body_data)
                    body_str = json.dumps(sanitised_body)
                else:
                    body_str = request.body.decode("utf-8", errors="replace")

                truncated_body = truncate_body(body_str)
                span.set_tag("http.request_body", truncated_body)
            except Exception as e:
                span.set_tag("http.request_body_error", str(e))

        # if hasattr(request, 'user') and request.user.is_authenticated:
        #     tracer.set_user({
        #         'id': str(request.user.pk),
        #         'username': getattr(request.user, 'username', ''),
        #         'email': getattr(request.user, 'email', ''),
        #     })

        return None

    async def _async_process_request(self, request):
        return await sync_to_async(self._sync_process_request)(request)

    def __call__(self, request):
        self._sync_process_request(request)
        response = self.get_response(request)
        return response

    async def __acall__(self, request):
        await self._async_process_request(request)
        response = await self.get_response(request)
        return response
