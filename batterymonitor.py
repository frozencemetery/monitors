#!/usr/bin/python3

import re
import subprocess
import sys

# Output from --monitor-detail.  The only real difference between this and -d
# is the formatting on device specification, so we just look for the paths
# directly.
"""
[14:12:59.232]	device changed:     /org/freedesktop/UPower/devices/battery_BAT0
  native-path:          BAT0
  vendor:               SMP
  model:                5B10W13900
  serial:               2204
  power supply:         yes
  updated:              vie 07 ago 2020 14:12:59 (0 seconds ago)
  has history:          yes
  has statistics:       yes
  battery
    present:             yes
    rechargeable:        yes
    state:               discharging
    warning-level:       none
    energy:              73.64 Wh
    energy-empty:        0 Wh
    energy-full:         81.16 Wh
    energy-full-design:  80.4 Wh
    energy-rate:         9.256 W
    voltage:             16.892 V
    time to empty:       8.0 hours
    percentage:          90%
    capacity:            100%
    technology:          lithium-polymer
    icon-name:          'battery-full-symbolic'
  History (charge):
    1596823979	90.000	discharging
  History (rate):
    1596823979	9.256	discharging

"""

devicere = re.compile(rb"/org/freedesktop/UPower/devices/(.*)$")
statere = re.compile(rb"state: +(.*)$")
pctre = re.compile(rb"percentage: +(\d+%)$")
ttlre = re.compile(rb"time to (empty|full): +(.*)$")

draw = True
reading = False
state = 'U'
pct = "0%"
ttl = "0 minutes"

seed_lines = subprocess.check_output(["upower", "-d"]).split(b"\n")

args = "stdbuf -oL upower --monitor-detail".split()
p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
assert(p.stdout) # appease mypy

while True:
    if draw:
        dttl = ttl if state != "F" else "∞"
        sys.stdout.write(f"{pct} {state} {dttl}\n")
        sys.stdout.flush()
        draw = False

    if len(seed_lines) > 0:
        line = seed_lines.pop(0)
    else:
        line = p.stdout.readline()
    assert(line != None)

    # Check if the device specified is changed
    m = devicere.search(line)
    if m:
        device = m.group(1)
        if device.startswith(b"battery"):
            reading = True
        else:
            reading = False
        continue

    if not reading:
        continue

    m = statere.search(line)
    if m:
        oldstate = state
        res = m.group(1)
        if res == b"charging":
            state = 'C'
        elif res == b"discharging":
            state = 'D'
        elif res == b"fully-charged":
            state = 'F'
        else:
            print(res)
            state = 'U'
            
        draw = state != oldstate
        continue

    m = pctre.search(line)
    if m:
        oldpct = pct
        pct = m.group(1).decode("utf-8")
        draw = pct != oldpct
        continue

    m = ttlre.search(line)
    if m:
        oldttl = ttl
        ttl = m.group(2).decode("utf-8")
        draw = ttl != oldttl
        continue
