#!/bin/env python3
import os
from pydoc import doc
import sys
from xdg import BaseDirectory
import subprocess
import argparse
from pathlib import Path
from redditUtils.imagedownloader import getImagesByNew, getImagesByHot, getImagesByTop


CACHE_DIR = os.path.join(BaseDirectory.xdg_cache_home,'pydit')
CONFIG_DIR = os.path.join(BaseDirectory.xdg_config_home,'pydit')

def directoryExists(dirname):
    d = Path(dirname)
    return d.exists() and d.is_dir()

def directoryIsEmpty(path):
    return len(os.listdir(path)) == 0

def cleanDirectory(path):
    for root, dirs, files in os.walk(path):
        for file in files:
            os.remove(os.path.join(root, file))

def setup():
    print("First time running? ok, creating cache and config directories.")
    os.mkdir(CACHE_DIR)
    os.mkdir(CONFIG_DIR)
    with open(os.path.join(CONFIG_DIR,'favorites.txt'),'w') as filp:
        filp.write('linuxmemes\n')
    print("Add your favorite subreddits on "+os.path.join(CONFIG_DIR,'favorites.txt'))

def getSubFromFavorites():
    subreddits = []
    i = 1
    with open(os.path.join(CONFIG_DIR,'favorites.txt'),'r') as filp:
        for line in filp :
            print("["+str(i)+"]"+line)
            if line[-1] == '\n':
                subreddits.append(line[:-1])
            else:
                subreddits.append(line)
            i = i+1
    subreddit = int(input('Please select the subreddit number, or zero to quit:'))
    if subreddit == 0:
        exit()
    return subreddits[subreddit-1]
def main():
    # Script title
    print("Gabbie's reddit media scraper")
    # Parse the command-line arguments
    parser = argparse.ArgumentParser(description="A reddit media scraper")
    parser.add_argument('-s', '--subreddit', dest='subreddit', help='Subreddit to be scraped',type=str)
    parser.add_argument('-m', '--mode', dest='mode', help='Mode that the scraper will use, options: new, top, hot', required = True, type=str)
    parser.add_argument('-l', '--limit', dest='limit', help='How many posts will be downloaded',default=100, type=int)
    parser.add_argument('-f', '--favorite', action= 'store_true', dest='favorite', help='Choose option from favorite file',default=False)
    args= parser.parse_args()
    # Check if the required directories exist on XDG config and cache user dirs
    if (not directoryExists(CACHE_DIR)) or (not directoryExists(CONFIG_DIR)):
        setup()
    # Check if the cache directory is empty, so we don't display repeated content from other runs
    if not directoryIsEmpty(CACHE_DIR):
        cleanDirectory(CACHE_DIR)
    # Check if we are using the favorite subreddit list
    if args.favorite :
        sub = getSubFromFavorites()
    else:
        sub = args.subreddit
    if sub == '' :
        print("No subreddit specified, quitting now.")
        exit()
    # Check the mode that we want
    if args.mode == 'new':
        getImagesByNew(sub,int(args.limit),CACHE_DIR)
    elif args.mode == 'top':
        getImagesByTop(sub,int(args.limit),CACHE_DIR)
    elif args.mode == 'hot':
        getImagesByHot(sub,int(args.limit),CACHE_DIR)
    #Check if there is some image to display
    if not directoryIsEmpty(CACHE_DIR):
        subprocess.run("sxiv -a "+'"'+CACHE_DIR+'/"*.*',shell=True)

if __name__ == '__main__':
    main()
