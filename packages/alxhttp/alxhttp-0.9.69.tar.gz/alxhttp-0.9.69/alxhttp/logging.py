import logging
from json import dumps
from time import time_ns
from typing import Any

from aiohttp.abc import AbstractAccessLogger
from aiohttp.web import BaseRequest, StreamResponse

from alxhttp.req_id import get_request, get_request_id, get_trace_id

_compact_separators = (',', ':')


def compact_json(obj: Any) -> str:
  return dumps(
    obj,
    indent=None,
    ensure_ascii=True,
    separators=_compact_separators,
  )


class JSONAccessLogger(AbstractAccessLogger):
  def __init__(self, logger: logging.Logger, log_format: str):
    super().__init__(logger, log_format)

  def log(
    self,
    request: BaseRequest,
    response: StreamResponse,
    time: float,
  ) -> None:
    """
    Taking some naming conventions from:
    https://github.com/opentracing/specification/blob/master/semantic_conventions.md
    """

    request_id = get_request_id(request)
    trace_id = get_trace_id(request)

    self.logger.info(
      compact_json(
        {
          'message': f'{request.method} {request.url.path} {response.status}',
          'duration': round(time, 8),
          'time_ns': time_ns(),
          'http': {
            'method': request.method,
            'status_code': response.status,
            'url': str(request.url),
          },
          'component': 'aiohttp',
          'request_id': request_id,
          'traceId': trace_id,
        }
      )
    )


class JSONLogFilter(logging.Filter):
  def filter(self, record: logging.LogRecord) -> bool:
    request = get_request()
    request_id = get_request_id(request) if request else None
    trace_id = get_trace_id(request) if request else None

    log_record = {
      'time_ns': time_ns(),
      'request_id': request_id,
      'traceId': trace_id,
    }

    if isinstance(record.msg, dict):
      log_record = {**log_record, **record.msg}
    else:
      log_record['message'] = record.msg

    record.msg = compact_json(log_record)

    return True


def get_json_server_logger() -> logging.Logger:
  logger = logging.getLogger('aiohttp.web')
  logger.addFilter(JSONLogFilter())

  return logger
