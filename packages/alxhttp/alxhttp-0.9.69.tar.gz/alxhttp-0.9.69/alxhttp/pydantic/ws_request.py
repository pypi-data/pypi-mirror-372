from typing import Type, TypeVar

import pydantic
from aiohttp import web

from alxhttp.pydantic.basemodel import BaseModel

WSRequestType = TypeVar('WSRequestType', bound='WSRequest')


class WSRequest[ServerMsgType, MatchInfoType, QueryType](BaseModel):
  _web_request: web.Request = pydantic.PrivateAttr()
  _ws: web.WebSocketResponse = pydantic.PrivateAttr()
  match_info: MatchInfoType
  query: QueryType

  @classmethod
  async def from_request(cls: Type[WSRequestType], request: web.Request) -> WSRequestType:
    m = cls.model_validate(
      {
        'match_info': request.match_info,
        'query': dict(request.query),
      }
    )
    m._web_request = request
    return m

  async def prepare_ws(self) -> None:
    self._ws = web.WebSocketResponse()
    await self._ws.prepare(self._web_request)

  async def send(self, msg: ServerMsgType) -> None:
    await self._ws.send_str(msg.model_dump_json())  # type: ignore
