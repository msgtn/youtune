import os
os.path.expanduser('~')
import sys
import youtube_dl
import eyed3
from selenium import webdriver as wd

import utils
from utils import PlaylistPage, ArtistPage

import fnmatch
import pickle

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-u','--url')
parser.add_argument('-p','--playlist', default='')
parser.add_argument('-a','--artist')
parser.add_argument('-s','--save_dir',default='')
parser.add_argument('-f','--format',default='mp3')
args = parser.parse_args()

def get_save_dir():
    try:
        with open('save_dir.txt', 'rb') as f:
            save_dir = pickle.load(f)
    except IOError:
        save_dir = str(input('Enter save directory path: '))

        with open('save_dir.txt', 'wb') as f:
            pickle.dump(save_dir, f)

    save_dir = save_dir.replace('~',os.environ['HOME'])
    print(save_dir)

    return save_dir

    

save_dir = args.save_dir
auto_add = save_dir==''
# default to being an iTunes directory
if save_dir == '':
    auto_add = get_save_dir()
else:
    auto_add = False
# save_dir = utils.get_save_dir() if save_dir == '' else save_dir

# get all the mp3 files already in the library
files = []
for root,subdir,fn in os.walk(save_dir):
    for f in fnmatch.filter(fn,'*.mp3'):
        files.append(f)

if args is None:
    # args.url = 'https://www.youtube.com/playlist?list=PLOav3VUypbiEg-hApJh1yzEs-jLV3b3Fz'
    args.url = 'https://www.youtube.com/playlist?list=PLOav3VUypbiG2hiOOX8tLoFNUDB-41wFF'

if args.playlist:
    print(PlaylistPage(args.playlist, files).get_videos(save_dir=save_dir, auto_add=auto_add))
elif args.artist:
    print(ArtistPage(args.artist, files).get_videos())
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

    PlaylistPage(playlist, files).get_videos(save_dir=save_dir)
