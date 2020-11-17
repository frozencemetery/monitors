#!/usr/bin/python3

import re
import subprocess
import sys

r = re.compile(r"\[(\d+)%\].*\[(on|off)\]$")

args = "stdbuf -oL alsactl monitor".split()
p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
assert(p.stdout) # appease mypy
while True:
    data = subprocess.check_output(["amixer", "get", "Master"])
    vline = data.rsplit(b"\n", 2)[-2].decode("utf-8")

    m = r.search(vline)
    assert(m)
    vol = m.group(1)
    onoff = m.group(2)
    muted = "%" if onoff == "on" else "M"

    sys.stdout.write(f"({vol}{muted})\n")
    sys.stdout.flush()

    p.stdout.readline()
