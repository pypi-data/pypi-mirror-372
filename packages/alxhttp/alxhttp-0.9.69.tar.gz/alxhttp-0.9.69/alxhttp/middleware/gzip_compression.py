from aiohttp import hdrs
from aiohttp.typedefs import Handler
from aiohttp.web import ContentCoding, Request, Response, StreamResponse, middleware


@middleware
async def gzip_compression(request: Request, handler: Handler) -> StreamResponse:
  resp = await handler(request)

  if isinstance(resp, Response):
    if 'gzip' in request.headers.get(hdrs.ACCEPT_ENCODING, '').lower():
      resp.headers[hdrs.CONTENT_ENCODING] = ContentCoding.gzip.value
      resp.enable_compression()

  return resp
