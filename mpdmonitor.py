#!/usr/bin/python3

import os
import random

from mpd import MPDClient

MPD_HOST="/run/mpd/socket"

os.chdir("/var/lib/mpd/music")

albums = []
artists = []

def load() -> None:
    artists = os.listdir()
    prune = []
    for artist in artists:
        try:
            aa = os.listdir(artist)
            for album in aa:
                albums.append(f"{artist}/{album}")
        except NotADirectoryError:
            prune.append(artist)

    for notartist in prune:
        artists.remove(notartist)

def maybe_enqueue():
    status = client.status()
    if status["state"] != "stop":
        return

    album = random.choice(albums)
    client.add(album)
    client.play()

def current() -> str:
    d = client.currentsong()
    disc_track = f'<fc=#4186be>{d["disc"]}-{d["track"]}</fc>'
    artist = f'<fc=#71BEBE>{d["artist"]}</fc>'
    title = f'<fc=#FFF796>{d["title"]}</fc>'
    album = f'<fc=#CF6171>{d["album"]}</fc>'
    return f'<{disc_track}> {artist} - "{title}" [{album}]'

load()
client = MPDClient()
client.connect(MPD_HOST)

maybe_enqueue()

print(current())
while True:
    events = client.idle("database", "playlist")
    if "database" in events:
        load()
    if "playlist" in events:
        maybe_enqueue()
