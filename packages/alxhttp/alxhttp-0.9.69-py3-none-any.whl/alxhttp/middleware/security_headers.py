from aiohttp.typedefs import Handler
from aiohttp.web import HTTPException, Request, StreamResponse, middleware
from multidict import CIMultiDict

from alxhttp.headers import content_security_policy


def _apply_security_header_defaults(headers: CIMultiDict[str]) -> None:
  if 'content-security-policy' not in headers:
    headers['content-security-policy'] = content_security_policy(default_src=['self'])
  if 'x-content-type-options' not in headers:
    headers['x-content-type-options'] = 'nosniff'
  if 'x-frame-options' not in headers:
    headers['x-frame-options'] = 'SAMEORIGIN'
  if 'referrer-policy' not in headers:
    headers['referrer-policy'] = 'strict-origin-when-cross-origin'


@middleware
async def security_headers(request: Request, handler: Handler) -> StreamResponse:
  try:
    resp = await handler(request)
    _apply_security_header_defaults(resp.headers)
    return resp
  except HTTPException as e:
    _apply_security_header_defaults(e.headers)
    raise
