#!/usr/bin/python3

import re
import subprocess
import sys
import time

r = re.compile(r"\[(\d+)%\].*\[(on|off)\]$")

# There's a race between WM start (when this script gets invoked by the
# statusbar) and pipewire start.  I can't ensure pipewire status (see below),
# so...
print("WAITING")
time.sleep(1)

args = "stdbuf -oL alsactl monitor".split()
p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
assert(p.stdout) # appease mypy
while True:
    try:
        data = subprocess.check_output(["amixer", "get", "Master"])
    except subprocess.CalledProcessError:
        print("RESTART")

        # --wait crashes and I'm not working bugs for an abuser
        subprocess.check_output(["systemctl", "--user", "restart", # "--wait",
                                 "wireplumber", "pipewire", "pipewire-pulse"])
        time.sleep(1)
        continue

    vline = data.rsplit(b"\n", 2)[-2].decode("utf-8")

    m = r.search(vline)
    assert(m)
    vol = m.group(1)
    onoff = m.group(2)
    muted = "%" if onoff == "on" else "M"

    if vol == "100":
        vol = "FF"
    elif len(vol) == 1:
        vol = f"0{vol}"

    sys.stdout.write(f"({vol}{muted})\n")
    sys.stdout.flush()

    p.stdout.readline()

print("DEAD")
