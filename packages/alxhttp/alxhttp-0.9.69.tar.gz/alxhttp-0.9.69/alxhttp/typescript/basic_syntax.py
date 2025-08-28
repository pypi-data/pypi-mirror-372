from typing import Any, Iterable, List


def upper_first(s: str) -> str:
  return s[0].upper() + s[1:]


def join(xs: Iterable[Any], sep: str = '\n') -> str:
  return sep.join([str(x) for x in xs])


def space(s: str) -> str:
  return f'\n{s}\n'


def field(xs: tuple[Any, Any]) -> str:
  return f'{xs[0]}: {xs[1]}'


def enlist(xs: Iterable[Any]) -> str:
  return f'[{join(xs, sep=",")}]'


def braces(xs: Iterable[Any], sep: str = '\n') -> str:
  return f'{{ {join(xs, sep=sep)} }}'


def obj_init(xs: Iterable[tuple[Any, Any]]) -> str:
  return braces([field(x) for x in xs], sep=',\n')


def parens(x: str) -> str:
  return f'({x})'


def python_to_js_string_template(s: str) -> str:
  return s.replace('{', '${')


def drop_leading_slash(s: str) -> str:
  if s[0] == '/':
    return s[1:]
  return s


def jsdoc(lines: List[str | List[str]]) -> str:
  result = ['/**']
  for line in lines:
    if isinstance(line, str):
      result.append(' * ' + line + '\n * ')
    else:
      result.append(join([' * ' + x for x in line]))
  result.append(' */')
  return join(result) + '\n'
