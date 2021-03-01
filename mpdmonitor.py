#!/usr/bin/python3

import os
import random
import sys

# no hints for mpd2 yet
from mpd import MPDClient # type: ignore

from typing import List

MPD_HOST="/run/mpd/socket"

f = open("/tmp/mpdmonitor.log", "w")
def log(s: str) -> None:
    f.write(s + "\n")
    f.flush()

log("Program start")

def load() -> List[str]:
    log("loading...")

    albums = []

    artists = os.listdir()
    for artist in artists:
        try:
            aa = os.listdir(artist)
            for album in aa:
                albums.append(f"{artist}/{album}")
        except NotADirectoryError:
            continue

    return albums

def maybe_enqueue(client: MPDClient, albums: List[str]) -> None:
    log("maybe_enqueue...")

    status = client.status()
    if status["state"] != "stop":
        return

    album = random.choice(albums)
    client.add(album)
    client.play()

def current(client: MPDClient) -> None:
    log("current...")

    d = client.currentsong()
    disc_track = f'<fc=#4186be>{d["disc"]}-{d["track"]}</fc>'
    artist = f'<fc=#71BEBE>{d["artist"]}</fc>'
    title = f'<fc=#FFF796>{d["title"]}</fc>'
    album = f'<fc=#CF6171>{d["album"]}</fc>'
    s = f'<{disc_track}> {artist} - "{title}" [{album}]\n'
    sys.stdout.write(s)
    sys.stdout.flush()

os.chdir("/var/lib/mpd/music")
albums = load()
client = MPDClient()
client.connect(MPD_HOST)

maybe_enqueue(client, albums)
current(client)

while events := client.idle("database", "playlist"):
    if "database" in events:
        albums = load()
    if "playlist" in events:
        maybe_enqueue(client, albums)
        current(client)

print("Goodbye!")
