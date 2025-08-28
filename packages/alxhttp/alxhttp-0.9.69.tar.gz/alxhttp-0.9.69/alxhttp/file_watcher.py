import os
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Callable, Dict, Generator

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

_watched_files: Dict[str, Callable[[], None]] = {}


def register_file_listener(file: str | Path, callback: Callable[[], None]) -> None:
  global _watched_files
  _watched_files[str(file)] = callback
  print(f'watching {file}')


def unregister_file_listener(
  file: str | Path,
) -> None:
  global _watched_files
  del _watched_files[str(file)]


class FSWatchHandler(FileSystemEventHandler):
  def on_modified(self, event: FileSystemEvent) -> None:
    if event.is_directory:
      return None
    modified_file = str(event.src_path)
    if callback := _watched_files.get(modified_file):
      try:
        callback()
        print(f'reloaded: {event.src_path}')
      except Exception as e:
        print(e)
    else:
      pass


@contextmanager
def watch_dir(watch_dir: Path | None = None) -> Generator[None, None, None]:
  if not watch_dir:
    watch_dir = Path(os.path.dirname(os.path.abspath(sys.argv[0])))
  event_handler = FSWatchHandler()
  observer = Observer()
  observer.schedule(event_handler, watch_dir, recursive=True)
  observer.start()
  try:
    print(f'watching {watch_dir}')
    yield
  finally:
    observer.stop()
    observer.join()
