import sys
from typing import TextIO

from alxhttp.pydantic.route import ErrorType
from alxhttp.pydantic.ws_route import WSRouteDetails
from alxhttp.typescript.wrappers.wrappers import gen_reader_imports, setup_ws_typeindex


def generate_ws_api_wrapper(rd: WSRouteDetails[ErrorType], base_url: str = 'http://127.0.0.1:8081/', out: TextIO = sys.stdout) -> None:
  gen_reader_imports(out)
  setup_ws_typeindex(rd, out)
