import asyncio
import os
from logging import Logger
from typing import Optional

import aiohttp
from aiohttp.typedefs import Middleware
from yarl import URL

try:
  from aws_xray_sdk.core import patch_all, xray_recorder
  from aws_xray_sdk.core.async_context import AsyncContext
  from aws_xray_sdk.ext.aiohttp.middleware import middleware as xray_middleware
except ImportError:
  xray_recorder = None
  xray_middleware = None


_imdsv2_md_url = URL('http://169.254.169.254/latest')


def get_xray_trace_id() -> Optional[str]:
  if xray_recorder is not None:
    try:
      trace = xray_recorder.get_trace_entity()
      if trace and trace.trace_id:
        return trace.trace_id
    except Exception:
      pass
  return None


def get_xray_middleware() -> Optional[Middleware]:
  return xray_middleware


async def _get_imdsv2_token(s: aiohttp.ClientSession) -> str:
  async with s.put(
    _imdsv2_md_url / 'api/token',
    headers={'X-aws-ec2-metadata-token-ttl-seconds': '21600'},
    timeout=3,
  ) as r:
    return await r.text()


async def get_ec2_ipv4() -> str:
  async with aiohttp.ClientSession() as s:
    token = await _get_imdsv2_token(s)

    async with s.get(
      _imdsv2_md_url / 'meta-data/local-ipv4',
      headers={'X-aws-ec2-metadata-token': token},
      timeout=3,
    ) as r:
      return await r.text()


async def init_xray(log: Logger, service_name: str, daemon_port: int = 40000) -> bool:
  try:
    ec2_ipv4 = await get_ec2_ipv4()

    patch_all()
    xray_recorder.configure(
      service=service_name,
      context=AsyncContext(),
      sampling=False,
      daemon_address=f'{ec2_ipv4}:{daemon_port}',
    )
    if log_group := os.environ.get('AWS_CLOUDWATCH_LOG_GROUP'):
      log_resources = xray_recorder._aws_metadata.setdefault('cloudwatch_logs', [{}])
      log_resources[0]['log_group'] = log_group

    log.info('XRay tracing enabled')
    return True
  except asyncio.TimeoutError:
    log.warning('Unable to get EC2 IP - XRay tracing disabled')
    return False
