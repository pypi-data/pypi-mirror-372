import asyncio
import sys
import traceback

from aiohttp.typedefs import Handler
from aiohttp.web import HTTPException, Request, StreamResponse, middleware

from alxhttp.json import json_error_response
from alxhttp.req_id import get_request_id


@middleware
async def unhandled_errors(request: Request, handler: Handler) -> StreamResponse:
  try:
    return await handler(request)
  except HTTPException:
    raise
  except Exception as e:
    exc = sys.exception()
    request.app.logger.error(
      {
        'request_id': get_request_id(request),
        'message': 'Unhandled Exception',
        'error': {'kind': e.__class__.__name__},
        'stack': repr(traceback.format_tb(exc.__traceback__)) if exc else '',
      }
    )

    # Be nice when debugging and dump the exception pretty-printed to the console
    loop = asyncio.get_running_loop()
    if loop.get_debug():
      request.app.logger.exception('Unhandled Exception')

    return json_error_response(request, 'Unhandled Exception', 500)
