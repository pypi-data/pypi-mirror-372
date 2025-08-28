from aiohttp.typedefs import Handler
from aiohttp.web import Request, StreamResponse, middleware


@middleware
async def g_state(request: Request, handler: Handler) -> StreamResponse:
  """
  Google login sets a "g_state" cookie that aiohttp cannot parse, but it is safe to remove
  """

  resp = await handler(request)

  resp.del_cookie('g_state')

  return resp
