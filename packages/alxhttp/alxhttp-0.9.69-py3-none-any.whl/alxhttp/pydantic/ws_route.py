from dataclasses import dataclass
from functools import partial
from typing import Any, Awaitable, Callable, List, Optional, Type, TypeVar

import humps
from aiohttp import web
from aiohttp.web_request import Request as WebRequest
from aiohttp.web_response import StreamResponse
from aiohttp.web_urldispatcher import UrlDispatcher
from pydantic import BaseModel

from alxhttp.pydantic.basemodel import Empty, ErrorModel
from alxhttp.pydantic.route import BaseRouteDetails
from alxhttp.pydantic.ws_request import WSRequest
from alxhttp.server import ServerType

ErrorType = TypeVar('ErrorType', bound=ErrorModel)

MatchInfoType = TypeVar('MatchInfoType', bound=BaseModel)
BodyType = TypeVar('BodyType', bound=BaseModel)
QueryType = TypeVar('QueryType', bound=BaseModel)
ClientMsgType = TypeVar('ClientMsgType')
ServerMsgType = TypeVar('ServerMsgType')


@dataclass
class WSRouteDetails[ErrorType](BaseRouteDetails[ErrorType]):
  client_msg: Type
  server_msg: Type


def get_ws_route_details(func: Callable) -> WSRouteDetails:
  return WSRouteDetails(
    name=func._alxhttp_route_name,
    match_info=func._alxhttp_match_info,
    query=func._alxhttp_query,
    client_msg=func._alxhttp_client_msg,
    server_msg=func._alxhttp_server_msg,
    ts_name=func._alxhttp_ts_name,
    errors=func._alxhttp_errors or [],
  )


class EmptyMsg(BaseModel):
  pass


def ws_route(
  name: str,
  client_msg: Type[ClientMsgType],
  server_msg: Type[ServerMsgType],
  ts_name: str | None = None,
  match_info: Type[MatchInfoType] = Empty,
  query: Type[QueryType] = Empty,
  errors: Optional[List[Type[ErrorType]]] = None,
):
  def decorator(
    func: Callable[
      [ServerType, WSRequest[server_msg, match_info, query]],
      Awaitable[web.WebSocketResponse],
    ],
  ):
    new_ts_name = ts_name
    if not new_ts_name:
      new_ts_name = humps.camelize(func.__name__)

    async def wrapper(server: ServerType, request: web.Request, *args: Any, **kwargs: Any) -> web.WebSocketResponse:
      vr = await WSRequest[server_msg, match_info, query].from_request(request)
      return await func(server, vr, *args, **kwargs)

    assert name == name.strip()

    setattr(wrapper, '_alxhttp_route_name', name)
    setattr(wrapper, '_alxhttp_match_info', match_info)
    setattr(wrapper, '_alxhttp_query', query)
    setattr(wrapper, '_alxhttp_client_msg', client_msg)
    setattr(wrapper, '_alxhttp_server_msg', server_msg)
    setattr(wrapper, '_alxhttp_ts_name', new_ts_name)
    setattr(wrapper, '_alxhttp_errors', errors)
    return wrapper

  return decorator


def add_ws_route(
  server: ServerType,
  router: UrlDispatcher,
  route_handler: Callable[[ServerType, WebRequest], Awaitable[StreamResponse]],
) -> None:
  route_details = get_ws_route_details(route_handler)
  handler = partial(route_handler, server)
  router.add_route('GET', route_details.name, handler)
  print(f'- GET[ws] {route_details.name}')
