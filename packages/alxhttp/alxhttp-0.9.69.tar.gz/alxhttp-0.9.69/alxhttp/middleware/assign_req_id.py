from aiohttp.typedefs import Handler
from aiohttp.web import Request, StreamResponse, middleware

from alxhttp.req_id import current_request, set_request_id


@middleware
async def assign_req_id(request: Request, handler: Handler) -> StreamResponse:
  set_request_id(request)
  token = current_request.set(request)
  try:
    return await handler(request)
  finally:
    current_request.reset(token)
