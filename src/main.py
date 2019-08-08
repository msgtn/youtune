import os
import sys
import youtube_dl
import eyed3
from selenium import webdriver as wd

import utils
from utils import PlaylistPage, ArtistPage

import pickle

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-u','--url')
parser.add_argument('-p','--playlist', default='')
parser.add_argument('-a','--artist')
args = parser.parse_args()
if args is None:
    # args.url = 'https://www.youtube.com/playlist?list=PLOav3VUypbiEg-hApJh1yzEs-jLV3b3Fz'
    args.url = 'https://www.youtube.com/playlist?list=PLOav3VUypbiG2hiOOX8tLoFNUDB-41wFF'

if args.playlist:
    print(PlaylistPage(args.playlist).get_videos())
elif args.artist:
    print(ArtistPage(args.artist).get_videos())
# default to download a playlist
else:
    print("Downloading playlists")
    try:
        with open('playlist.txt', 'rb') as f:
            playlist = pickle.load(f)
    except IOError:
        playlist = raw_input('Enter playlist URL: ')

        with open('playlist.txt', 'a+') as f:
            pickle.dump(playlist, f)

    PlaylistPage(playlist).get_videos()
