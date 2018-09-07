#!/bin/bash

export MPD_HOST='/run/mpd/socket'

function lpad {
    word="$1"
    while [ ${#word} -lt $2 ]; do
        word="$3$word"
    done
    echo " (${word})"
}

# "##" escaped by mpc to "#"
if [ x"$1" == x"xmobar" ]; then
    string="<<fc=##4186be>%disc%-%track%</fc>> <fc=##71BEBE>%artist%</fc> - \"<fc=##FFF796>%title%</fc>\" #[<fc=##CF6171>%album%</fc>#]"
elif [ x"$1" == x"dzen" ] || [ x"$1" == x"dzen2" ]; then
    string="^fg(##71BEBE)%artist%^fg() - \"^fg(##FFF796)%title%^fg()\" #[^fg(##CF6171)%album%^fg()#]"
else
    string="<%disc%-%track% %artist%> - \"%title%\" #[%album%#]"
fi

while true; do
    mpc current -f "${string}" | tr -d '\n'
    lpad "$(amixer get Master | tail -n 1 | awk '{print $4}' | sed -e 's/\[\|\]//g' -e 's/100/FF/g')" 3 0

    mpc idle >/dev/null
    if [ -z "$(mpc playlist)" ]; then
        cd /var/lib/mpd/music; find "$(find -maxdepth 1 -mindepth 1 -type d  | shuf | head -n1)" -maxdepth 1 -mindepth 1 -type d | cut -b 1-2 --complement | shuf | head -n1 | mpc --wait add
        mpc play
    fi
done
