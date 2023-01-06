"""
Categorize the crashes.
"""

import fire
import subprocess

from utils import afl


def run_target_and_get_error(cmd):
  with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True) as pipes:
    _, std_err = pipes.communicate()
  return std_err.decode("utf-8")


def get_assertion_msg(msg):
  for line in msg.split("\n"):
    if "Assertion" in line or "Seg" in line or "==ERROR" in line:
      return line
  return ""


def triage(cmd, path):
  crashes = afl.get_all_crashes(path)
  result = {}
  for crash in crashes:
    if "@@" in cmd:
      tmp_cmd = cmd.replace("@@", repr(crash))
    else:
      tmp_cmd = f"{cmd} <{repr(crash)}"
    msg = get_assertion_msg(run_target_and_get_error(tmp_cmd))
    if not msg:
      continue
    result[msg] = crash
  for key, value in result.items():
    print(key, value)


if __name__ == "__main__":
  fire.Fire(triage)
