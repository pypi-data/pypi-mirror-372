from aiohttp.web_exceptions import HTTPBadRequest as WebHTTPBadRequest

from alxhttp.json import json_dumps
from alxhttp.req_id import get_request, get_request_id


class HTTPBadRequest(WebHTTPBadRequest):
  """
  This exists for cases where you don't want to make a pydantic model to
  represent the exception, but the pydantic approach is the preferred approach
  """

  def __init__(self, message: dict):
    request = get_request()
    request_id = get_request_id(request) if request else None

    super().__init__(
      text=json_dumps(
        {
          'error': 'Bad Request',
          'status_code': 400,
          'request_id': request_id,
        }
        | message
      ),
      content_type='application/json',
    )
