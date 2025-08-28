import json
import logging
from typing import Iterable

from aiohttp.typedefs import Handler, Middleware
from aiohttp.web import Request, Response, StreamResponse, middleware
from aiohttp.web_exceptions import HTTPException

from alxhttp.json import json_default
from alxhttp.req_id import get_request_id


def req_res_logger(status_codes: Iterable[int] | None = None) -> Middleware:
  """
  Factory function that creates a middleware to log request/response as pretty-printed JSON
  when certain status codes are returned.

  Args:
    status_codes: List of HTTP status codes to log. Defaults to [400].

  Returns:
    Middleware function configured with the specified status codes.

  Usage:
    # Log only 400 status codes (default)
    app = web.Application(middlewares=[req_res_logger()])

    # Log multiple status codes
    app = web.Application(middlewares=[req_res_logger([400, 404, 500])])
  """
  if status_codes is None:
    status_codes = [400]

  @middleware
  async def _req_res_logger_middleware(request: Request, handler: Handler) -> StreamResponse:
    logger = logging.getLogger('alxhttp.req_res_logger')
    req_id = get_request_id(request)

    # Capture request body
    request_body = None
    try:
      body_text = await request.text()
      if body_text:
        request_body = json.loads(body_text)
    except Exception:
      request_body = body_text if 'body_text' in locals() else None

    try:
      resp = await handler(request)

      # Check if response status should be logged
      if isinstance(resp, Response) and resp.status in status_codes:
        await _log_request_response(logger, req_id, request, resp, request_body)

      return resp

    except HTTPException as e:
      # Check if exception status should be logged
      if e.status in status_codes:
        await _log_request_response_exception(logger, req_id, request, e, request_body)
      raise

  return _req_res_logger_middleware


async def _log_request_response(logger: logging.Logger, req_id: str, request: Request, response: Response, request_body: str | dict | None) -> None:
  """Log request and response data as pretty JSON"""

  # Parse response body if possible
  response_body = None
  try:
    if hasattr(response, 'body') and response.body:
      response_body = json.loads(response.body) if isinstance(response.body, bytes) else response.body
  except Exception:
    response_body = str(response.body) if hasattr(response, 'body') else None

  log_data = {
    'req_id': req_id,
    'status': response.status,
    'request': {
      'method': request.method,
      'url': str(request.url),
      'headers': dict(request.headers),
      'query': dict(request.query),
      'match_info': dict(request.match_info),
      'body': request_body,
    },
    'response': {
      'status': response.status,
      'headers': dict(response.headers),
      'body': response_body,
    },
  }

  logger.info(f'Status {response.status} - Request/Response:\n' + json.dumps(log_data, indent=2, sort_keys=True, default=json_default))


async def _log_request_response_exception(logger: logging.Logger, req_id: str, request: Request, exception: HTTPException, request_body: str | dict | None) -> None:
  """Log request and exception data as pretty JSON"""

  # Parse exception body if possible
  exception_body = None
  try:
    if exception.text:
      exception_body = json.loads(exception.text)
  except Exception:
    exception_body = exception.text

  log_data = {
    'req_id': req_id,
    'status': exception.status,
    'request': {
      'method': request.method,
      'url': str(request.url),
      'headers': dict(request.headers),
      'query': dict(request.query),
      'match_info': dict(request.match_info),
      'body': request_body,
    },
    'exception': {
      'status': exception.status,
      'reason': exception.reason,
      'headers': dict(exception.headers),
      'body': exception_body,
    },
  }

  logger.info(f'Status {exception.status} - Request/Exception:\n' + json.dumps(log_data, indent=2, sort_keys=True, default=json_default))
