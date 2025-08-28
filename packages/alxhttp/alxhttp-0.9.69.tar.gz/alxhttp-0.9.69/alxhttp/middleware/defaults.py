from typing import List

from aiohttp.typedefs import Middleware

from alxhttp.middleware.assign_req_id import assign_req_id
from alxhttp.middleware.ensure_json_errors import ensure_json_errors
from alxhttp.middleware.pydantic_validation import pydantic_validation
from alxhttp.middleware.security_headers import security_headers
from alxhttp.middleware.unhandled_errors import unhandled_errors
from alxhttp.xray import get_xray_middleware


def default_middleware(include_xray: bool = False) -> List[Middleware]:
  middlewares: List[Middleware] = [
    assign_req_id,
    security_headers,
    unhandled_errors,
    ensure_json_errors,
    pydantic_validation,
  ]

  if include_xray:
    xray_middleware = get_xray_middleware()
    if xray_middleware is not None:
      middlewares.insert(0, xray_middleware)

  return middlewares
