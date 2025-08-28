import json
import os
from datetime import datetime, timezone

from aiohttp.typedefs import Handler
from aiohttp.web import Request, Response, StreamResponse, middleware
from aiohttp.web_exceptions import HTTPException

from alxhttp.json import json_default
from alxhttp.req_id import get_request_id


@middleware
async def save_json(request: Request, handler: Handler) -> StreamResponse:
  """
  Save all requests/responses to json locally
  """
  ts = int(datetime.now(tz=timezone.utc).timestamp())

  req_id = get_request_id(request)
  body = None
  try:
    body = await request.text()
    body = json.loads(body)
  except Exception:
    pass
  os.makedirs('output', exist_ok=True)
  with open(f'output/{ts}_{req_id}.req.json', mode='x') as f:
    f.write(
      json.dumps(
        {
          'req_id': req_id,
          'url': request.url,
          'match_info': dict(request.match_info),
          'headers': dict(request.headers),
          'cookies': dict(request.cookies),
          'query': dict(request.query),
          'body': body,
        },
        indent=2,
        sort_keys=True,
        ensure_ascii=True,
        default=json_default,
      )
    )

  try:
    resp = await handler(request)
  except HTTPException as e:
    body = e.text
    try:
      body = json.loads(body) if body else None
    except Exception:
      pass
    with open(f'output/{ts}_{req_id}.resp.json', mode='x') as f:
      f.write(
        json.dumps(
          {
            'req_id': req_id,
            'body': body,
            'headers': dict(e.headers),
          },
          indent=2,
          sort_keys=True,
          ensure_ascii=True,
          default=json_default,
        )
      )
    raise

  if isinstance(resp, Response):
    with open(f'output/{ts}_{req_id}.resp.json', mode='x') as f:
      body = None
      try:
        body = resp.body
        body = json.loads(resp.body) if isinstance(resp.body, bytes) else None
      except Exception:
        pass
      f.write(
        json.dumps(
          {
            'req_id': req_id,
            'body': body,
            'headers': dict(resp.headers),
            'cookies': dict(resp.cookies),
          },
          indent=2,
          sort_keys=True,
          ensure_ascii=True,
          default=json_default,
        )
      )
  else:
    with open(f'output/{ts}_{req_id}.resp.json', mode='x') as f:
      f.write(
        json.dumps(
          {
            'req_id': req_id,
          }
        )
      )

  return resp
