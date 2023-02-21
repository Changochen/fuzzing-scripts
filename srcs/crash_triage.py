"""
Categorize the crashes.
"""

import fire
import subprocess
import re
import os

from utils import afl


class ErrorInfo(object):

  def __init__(self, error_type=None, error_loc=None, error_msg=None, bt=None):
    self.error_type = error_type
    self.error_loc = error_loc
    self.error_msg = error_msg
    self.bt = bt

  def __str__(self):
    return f"Error type: {self.error_type}, loc: {self.error_loc}, msg: {self.error_msg}"


def run_target_and_get_error(cmd):
  with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True) as pipes:
    _, std_err = pipes.communicate()
  return std_err.decode("utf-8")


def extract_asan_error(msg):
  result = ErrorInfo()
  asan_type_patterns = [r"SUMMARY: AddressSanitizer: ([^\s]+) ([^\s]+) in (.+)",
  "SUMMARY: AddressSanitizer: (SEGV)( )([^\s]+)"]
  for line in msg.split("\n"):
    if "SUMMARY" in line:
      for pattern in asan_type_patterns:
        match = re.search(pattern, line)
        if not match:
            continue
        result.error_type = match.group(1)
        result.error_loc = match.group(3)
        result.error_msg = match.group(2)
        return result
      print(msg)
      assert match
  assert False


def get_err_info(msg):
  #assertion_pattern = "(Assertion .* failed)"
  if "==ERROR: AddressSanitizer" in msg:
    return extract_asan_error(msg)
  for line in msg.split("\n"):
    if "Assertion" in line and "failed" in line:
      component = line.split(": ")
      result = ErrorInfo()
      result.error_type = "Assertion failure"
      result.error_loc = component[3]
      result.error_msg = component[2]
      return result
    if "Seg" in line or "==ERROR" in line:
      print(msg)
      assert False
      result = ErrorInfo()
      result.error_type = line
      result.error_loc = line
      result.error_msg = line
      return result
  return None


def triage(cmd, path):
  crashes = afl.get_all_crashes(path)
  result = {}
  for crash in crashes:
    if "@@" in cmd:
      tmp_cmd = cmd.replace("@@", repr(crash))
    else:
      tmp_cmd = f"{cmd} <{repr(crash)}"
    msg = get_err_info(run_target_and_get_error(tmp_cmd))
    if not msg:
      continue
    if msg.error_type not in result:
      result[msg.error_type] = {}
    result[msg.error_type][msg.error_loc] = crash
  for key, value in result.items():
    print(f"Error type: {key}")
    for idx, (error_loc, file_path) in enumerate(value.items()):
      print("+" * 40)
      print(f"{idx}: {error_loc} at {file_path}")
    print("=" * 40)


if __name__ == "__main__":
  fire.Fire(triage)
