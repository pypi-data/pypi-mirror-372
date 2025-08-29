import json
import logging

from requests import Response, RequestException

from platform_sdk.shared.constants import UNKNOWN


def log_exception(exc: Exception, logger=None):
    logger = logger if logger else logging.getLogger()

    msg = {
        "exception": {
            "exception_type": type(exc).__name__,
            "dependency_name": getattr(exc, "dependency_name", UNKNOWN),
            "stringified": str(exc),
        }
    }

    add_http_data(exc, msg)

    json_log = json.dumps(msg)
    logger.exception(json_log)


def add_http_data(exc, msg):
    if hasattr(exc, "request") or hasattr(exc, "response"):
        msg["exception"]["http"] = {}
    if hasattr(exc, "request"):
        add_request_data(exc, msg)
    if hasattr(exc, "response"):
        add_response_data(exc, msg)


def add_request_data(exc, msg):
    request = getattr(exc, "request")
    headers = getattr(request, "headers", None)

    request_body = getattr(request, "body", None)
    parsed_request = _parse_request(request_body)

    msg["exception"]["http"]["url"] = getattr(request, "url", None)
    msg["exception"]["http"]["request"] = {
        "headers": dict(headers) if headers else None,
        "method": getattr(request, "method", None)
    }

    if parsed_request.get('body'):
        msg["exception"]["http"]["request"]["body"] = parsed_request['body']

    if parsed_request.get('json'):
        msg["exception"]["http"]["request"]["json"] = parsed_request['json']


def _parse_request(request_body):
    parsed_request = {}

    if not request_body:
        return parsed_request

    if isinstance(request_body, bytes):
        request_body = request_body.decode("utf-8")

    parsed_request['body'] = request_body
    try:
        parsed_request['json'] = json.loads(request_body)
    except json.JSONDecodeError:
        pass

    return parsed_request


def add_response_data(exc, msg):
    response = getattr(exc, "response")
    headers = getattr(response, "headers", None)

    msg["exception"]["http"]["response"] = {
        "body": getattr(response, "text", None),
        "status_code": getattr(response, "status_code", UNKNOWN),
        "headers": dict(headers) if headers else None,
    }

    # noinspection PyBroadException
    try:
        msg["exception"]["http"]["response"]["json"] = response.json()
    except Exception:
        pass


def raise_for_status_with_dependency_name(response: Response, dependency_name: str):
    try:
        response.raise_for_status()
    except RequestException as request_error:
        request_error.dependency_name = dependency_name
        raise request_error
