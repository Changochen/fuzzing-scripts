"""
Utils for AFL like fuzzers.
"""
import os
from typing import List, Union


def fast_scandir(dname):
  """Get all directories."""
  subfolders = [f.path for f in os.scandir(dname) if f.is_dir()]
  for dirname in list(subfolders):
    if not str(dirname).endswith("queue") and not str(dirname).endswith("hangs"):
      subfolders.extend(fast_scandir(dirname))
  return subfolders


def get_all_queue_dir(dname, skip="") -> List[str]:
  """Get all queue dir"""
  all_folders = fast_scandir(dname)
  return [folder for folder in all_folders if str(folder).endswith("queue") and skip in str(folder)]


def get_all_fuzzer_stats(dname: str) -> List[str]:
  all_folders = fast_scandir(dname)
  return [
      f"{folder}/fuzzer_stats" for folder in all_folders if os.path.exists(f"{folder}/fuzzer_stats")
  ]


def get_stat_by_name(dname: str, stat: str) -> List[Union[str, int]]:
  all_stat_files = get_all_fuzzer_stats(dname)
  result = []
  for stat_file in all_stat_files:
    with open(stat_file, "r", encoding="utf-8") as f:
      for line in f.readlines():
        if stat in line:
          data: Union[str, int] = line.split(":")[1].strip()
          try:
            data = int(data)
          except ValueError:
            pass
          result.append(data)
  return result


def get_all_crashes_dir(dname) -> List[str]:
  """Get all queue dir"""
  all_folders = fast_scandir(dname)
  return [folder for folder in all_folders if str(folder).endswith("crashes")]


def get_all_crashes(dname) -> List[str]:
  all_crash_dir = get_all_crashes_dir(dname)
  result = []
  for crash_dir in all_crash_dir:
    for crash in os.listdir(crash_dir):
      result.append(os.path.join(crash_dir, crash))
  return result
