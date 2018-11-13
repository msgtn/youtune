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
parser.add_argument('-p','--playlist')
parser.add_argument('-a','--artist')
args = parser.parse_args()
if args is None:
    args.url = 'https://www.youtube.com/playlist?list=PLOav3VUypbiEg-hApJh1yzEs-jLV3b3Fz'

if args.playlist:
    print(PlaylistPage(args.playlist).get_videos())
if args.artist:
    print(ArtistPage(args.artist).get_videos())
