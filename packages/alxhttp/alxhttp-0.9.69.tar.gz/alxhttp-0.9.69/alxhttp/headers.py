from typing import Iterable, List, Union


class Unspecified:
  pass


_UnspecifiedAllowList = Unspecified()
_UnspecifiedSourceList = Unspecified()


Directives = List[str]
Sources = List[str]
AllowList = Union[Directives, Unspecified]
SourceList = Union[Sources, Unspecified]

raw_directives = {'*', 'src', 'self'}


def _flatten_directives(ds: Directives) -> str:
  return ' '.join(d if d in raw_directives else f'"{d}"' for d in ds)


def _handle_directive_allowlist(feature: AllowList, feature_name: str, result: List[str]):
  if isinstance(feature, Iterable):
    result.append(f'{feature_name}=({_flatten_directives(feature)})')


def permissions_policy(
  autoplay: AllowList = _UnspecifiedAllowList,
  fullscreen: AllowList = _UnspecifiedAllowList,
) -> str:
  result = []
  _handle_directive_allowlist(autoplay, 'autoplay', result)
  _handle_directive_allowlist(fullscreen, 'fullscreen', result)
  return ', '.join(result)


quoted_sources = {
  'self',
  'unsafe-eval',
  'wasm-unsafe-eval',
  'unsafe-hashes',
  'unsafe-inline',
  'none',
  'strict-dynamic',
  'report-sample',
  'inline-speculation-rules',
}


def _should_quote(s: str) -> bool:
  if s in quoted_sources:
    return True
  bits = s.split('-')
  if bits[0] in {'nonce', 'sha256', 'sha384', 'sha512'}:
    return True

  return False


def _flatten_sources(ss: Sources) -> str:
  return ' '.join(f"'{s}'" if _should_quote(s) else s for s in ss)


def _handle_sourcelist(sources: SourceList, policy_name: str, result: List[str]) -> None:
  if isinstance(sources, Iterable):
    result.append(f'{policy_name} {_flatten_sources(sources)}')


def content_security_policy(
  default_src: SourceList = _UnspecifiedSourceList,
  font_src: SourceList = _UnspecifiedSourceList,
  img_src: SourceList = _UnspecifiedSourceList,
  media_src: SourceList = _UnspecifiedSourceList,
  script_src: SourceList = _UnspecifiedSourceList,
  style_src: SourceList = _UnspecifiedSourceList,
  worker_src: SourceList = _UnspecifiedSourceList,
  object_src: SourceList = _UnspecifiedSourceList,
) -> str:
  result = []
  _handle_sourcelist(default_src, 'default-src', result)
  _handle_sourcelist(font_src, 'font-src', result)
  _handle_sourcelist(img_src, 'img-src', result)
  _handle_sourcelist(media_src, 'media-src', result)
  _handle_sourcelist(script_src, 'script-src', result)
  _handle_sourcelist(style_src, 'style-src', result)
  _handle_sourcelist(worker_src, 'worker-src', result)
  _handle_sourcelist(object_src, 'object-src', result)
  return '; '.join(result)
