from typing import Tuple

import aiohttp
import aiohttp.abc
from multidict import CIMultiDict


class MultipartBytesWriter(aiohttp.abc.AbstractStreamWriter):
  data: bytes = b''

  async def write(self, chunk: bytes) -> None:
    self.data += chunk

  async def write_eof(self, chunk: bytes = b'') -> None:
    raise NotImplementedError()  # pragma: nocover

  async def drain(self) -> None:
    raise NotImplementedError()  # pragma: nocover

  def enable_compression(self, encoding: str = 'deflate') -> None:
    raise NotImplementedError()  # pragma: nocover

  def enable_chunking(self) -> None:
    raise NotImplementedError()  # pragma: nocover

  async def write_headers(self, status_line: str, headers: 'CIMultiDict[str]') -> None:
    raise NotImplementedError()  # pragma: nocover

  async def get_ct_and_bytes(self, mpw: aiohttp.MultipartWriter) -> Tuple[str, bytes]:
    await mpw.write(self)
    return (f'multipart/text; boundary={mpw.boundary}', self.data)
