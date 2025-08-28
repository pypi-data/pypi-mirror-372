import asyncio
import json
from typing import Any

from aiohttp import StreamReader
from aiohttp.base_protocol import BaseProtocol


class DummyBaseProtocol(BaseProtocol):
  def __init__(self, loop: asyncio.AbstractEventLoop):
    super().__init__(loop)

  # def connection_made(self, transport):
  # def data_received(self, data):
  # def eof_received(self):


class BytesStreamReader(StreamReader):
  def __init__(self, data: bytes, loop: asyncio.AbstractEventLoop | None = None):
    if loop is None:
      loop = asyncio.get_running_loop()
    super().__init__(DummyBaseProtocol(loop), 2**16, loop=loop)
    self._data = data

  # async def _wait_for_data(self, func_name: str):
  # def feed_eof(self):
  # def is_eof(self):
  # def at_eof(self):

  async def read(self, n: int = -1) -> bytes:
    if not self._data:
      return b''

    if n >= 0:
      chunk = self._data[:n]
      self._data = self._data[n:]
    else:
      chunk = self._data
      self._data = b''

    return chunk

  async def readany(self) -> bytes:
    return await self.read()

  async def readline(self) -> bytes:
    newline_pos = self._data.find(b'\n')
    if newline_pos == -1:
      return await self.readany()

    chunk = self._data[: newline_pos + 1]
    self._data = self._data[newline_pos + 1 :]
    return chunk


class JSONStreamReader(BytesStreamReader):
  def __init__(self, data: Any):
    super().__init__(json.dumps(data).encode())
