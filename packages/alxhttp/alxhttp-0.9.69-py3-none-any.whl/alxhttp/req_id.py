import contextvars
import random

from aiohttp.web import BaseRequest

from alxhttp.xray import get_xray_trace_id

__req_id_key = '__req_id_middleware'
__trace_id_key = '__req_id_middleware_trace_id'

current_request = contextvars.ContextVar('current_request')


def _req_id() -> str:
  r = random.getrandbits(128)
  return f'{r:016x}'


def get_request() -> BaseRequest:
  req: BaseRequest = current_request.get()
  return req


def get_request_id(request: BaseRequest) -> str:
  return request.get(__req_id_key, '')


def get_trace_id(request: BaseRequest) -> str:
  return request.get(__trace_id_key, '')


def set_request_id(request: BaseRequest) -> None:
  trace_id = get_xray_trace_id()

  request[__req_id_key] = _req_id()
  request[__trace_id_key] = trace_id
