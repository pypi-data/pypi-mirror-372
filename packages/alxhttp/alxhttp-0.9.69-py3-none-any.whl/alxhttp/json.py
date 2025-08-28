import json
from datetime import datetime
from typing import Any

import pydantic
from aiohttp import web
from aiohttp.web import Request, Response

from alxhttp.req_id import get_request_id


def json_default(x: Any) -> Any:
  if isinstance(x, datetime):
    return x.timestamp()
  elif isinstance(x, pydantic.BaseModel):
    return x.model_dump(mode='json')
  return str(x)


def json_dumps(x: Any) -> str:
  return json.dumps(x, indent=0, sort_keys=True, default=json_default)


def json_response(x: Any, status: int = 200) -> web.Response:
  return web.json_response(text=json_dumps(x), status=status)


def json_error_response(req: Request, error: str, status_code: int, rest: dict | None = None) -> Response:
  rest = rest or {}

  return json_response(
    {
      'error': error,
      'status_code': status_code,
      'request_id': get_request_id(req),
    }
    | rest,
    status=status_code,
  )
