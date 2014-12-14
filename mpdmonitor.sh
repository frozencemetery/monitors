#!/bin/bash

export MPD_HOST='/home/frozencemetery/.mpd/socket'

function lpad {
    word="$1"
    while [ ${#word} -lt $2 ]; do
        word="$3$word";
    done;
    echo " (${word})";
}

while true; do
    # "##" escaped by mpc to "#"
    mpc current -f "<fc=##71BEBE>%artist%</fc> - \"<fc=##FFF796>%title%</fc>\" #[<fc=##CF6171>%album%</fc>#]" | tr -d '\n'
    lpad "$(amixer get Master | tail -n1 | awk '{print $4$6}' | tr -d '[]' | sed -e 's/on//g' -e 's/%off/M/g' -e 's/100/FF/g')" 3 0;
    mpc idle >/dev/null
    if [ -z "$(mpc playlist)" ]; then
        cd /home/frozencemetery/Music; find "$(find -maxdepth 1 -mindepth 1 -type d  | shuf | head -n1)" -maxdepth 1 -mindepth 1 -type d | cut -b 1-2 --complement | shuf | head -n1 | mpc --wait add
        mpc play
    fi
done
