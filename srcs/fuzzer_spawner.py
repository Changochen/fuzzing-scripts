"""
Run multiple fuzzer instances in a tmux session.
"""
import libtmux
import os
import argparse
from datetime import date
import time


def ap(a):
  return os.path.abspath(a)


if __name__ == "__main__":
  args = argparse.ArgumentParser()
  args.add_argument("-f", "--fuzzer", help="path of the fuzzer", required=True)
  args.add_argument("-o", "--output", help="path of the output result", required=True)
  args.add_argument("-i", "--input", help="path of the input seed", required=True)
  args.add_argument("-p", "--program", help="path of the fuzzed program", required=True)
  args.add_argument("-n", "--number", help="the number of fuzzers", required=True)
  args.add_argument("-s", "--session", help="tmux session name", required=True)
  args.add_argument("-e", "--extra", help="extra args for the fuzzer", required=False, default="")
  args.add_argument("-u", "--unique", help="unique file name", required=False, default="")
  args.add_argument("--env", help="Environment variable.", required=False, default="")
  args.add_argument("--no_unlimited_mem",
                    help="Whether not run with -m none",
                    required=False,
                    default=False)

  arg_result = args.parse_args()

  today = str(date.today())
  #print(today)
  server = libtmux.Server()
  #print(server.list_sessions())
  session = server.new_session(session_name=arg_result.session)
  #print(session)

  nums = int(arg_result.number)

  print("Spawning fuzzer....")
  for i in range(nums):
    win = session.new_window(attach=False)
    pane = win.attached_pane

    if not os.path.exists(arg_result.output):
      os.mkdir(arg_result.output)
    output_dir = ap(arg_result.output) + "/" + today
    mem_none = "-m none"
    if arg_result.no_unlimited_mem:
      mem_none = ""
    if i == 0:
      cmd = f"{arg_result.env} {ap(arg_result.fuzzer)} {mem_none} -M master -i {arg_result.input} -o {output_dir} {arg_result.extra} --  {ap(arg_result.program)}"
    else:
      cmd = f"{arg_result.env} {ap(arg_result.fuzzer)} {mem_none} -S slave{i} -i {arg_result.input} -o {output_dir} {arg_result.extra} --   {ap(arg_result.program)}"
    if "@@@" in cmd and arg_result.unique:
      cmd = cmd.replace("@@@", arg_result.unique + str(i))
    print("COMMAND: ", cmd)
    pane.send_keys(cmd)
    time.sleep(1)
  print(f"Done! Check tmux session {arg_result.session}")
