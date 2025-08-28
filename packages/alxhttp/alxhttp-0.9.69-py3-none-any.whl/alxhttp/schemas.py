import secrets

import pydantic


def prefixed_id(prefix: str, num_hexchars: int = 12) -> pydantic.StringConstraints:
  return pydantic.StringConstraints(pattern=rf'^{prefix}[0-9A-Fa-f]{{{num_hexchars}}}$')


def gen_prefixed_id(prefix: str, num_bytes: int = 12) -> str:
  return f'{prefix}{secrets.token_bytes(num_bytes).hex()}'
