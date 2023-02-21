"""
Check whether there is new crashes periodically.
"""
import fire
import os
import time
from pathlib import Path

from utils import afl


def find_new_crashes(check_path, cache_path):
  crashes = afl.get_all_crashes(check_path)
  Path(cache_path).touch()

  if not crashes:
    return []

  with open(cache_path, encoding="utf-8") as f:
    previous_crashes = set(line.strip() for line in f.readlines())

  result = []
  for crash in crashes:
    crash = crash.strip()
    if crash not in previous_crashes:
      result.append(crash)

  return result


def append_to_cache(cache_path, new_crashes):
  with open(cache_path, "a", encoding="utf-8") as f:
    f.write("\n".join(new_crashes) + "\n")


def check_at_interval(interval, check_path, cache_path):
  while True:
    new_crashes = find_new_crashes(check_path, cache_path)
    if new_crashes:
      append_to_cache(cache_path, new_crashes)
      with open("/tmp/new_crashes", "w", encoding="utf-8") as f:
        new_crashes_str = "\n".join(new_crashes)
        content = f"Found {len(new_crashes)} crashes.\n{new_crashes_str}"
        f.write(content)
      os.system("mail /tmp/new_crashes")
    time.sleep(interval)


if __name__ == "__main__":
  fire.Fire(check_at_interval)
