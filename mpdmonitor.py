#!/usr/bin/python3

import os
import random
import sys
import traceback

# no hints for mpd2 yet
from mpd import MPDClient # type: ignore

from typing import List

MPD_HOST = "~/.mpd/socket"

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

    try:
        disc_track = f'<fc=#4186be>{d["disc"]}-{d["track"]}</fc>'
        artist = f'<fc=#71BEBE>{d["artist"]}</fc>'
        title = f'<fc=#FFF796>{d["title"]}</fc>'
        album = f'<fc=#CF6171>{d["album"]}</fc>'
        s = f'<{disc_track}> {artist} - "{title}" [{album}]\n'
    except KeyError:
        s = f'Bad tags on: {d["file"]}\n'

    sys.stdout.write(s)
    sys.stdout.flush()

if __name__ == "__main__":
    os.chdir("/var/lib/mpd/music")
    albums = load()

    i = 0
    while True:
        log("loop!")
        i += 1
        if i > 20:
            log("Too many connection failures; goodbye!")
            print(":ded:")
            exit(1)

        try:
            client = MPDClient()
            client.connect(os.path.expanduser(MPD_HOST))

            maybe_enqueue(client, albums)
            current(client)

            while events := client.idle("database", "playlist"):
                if "database" in events:
                    albums = load()
                if "playlist" in events:
                    maybe_enqueue(client, albums)
                    current(client)

        except ConnectionError:
            log(f"connection died; retrying {i}")
        except Exception:
            log(traceback.format_exc())
            log(f"other failure; retrying {i}")
        else:
            log(f"empty event list?  Hanging up {i}")
