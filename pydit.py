#!/bin/env python3
import os
import sys
import xdg
import subprocess
from pathlib import Path
from redditUtils.imagedownloader import getImagesByNew, getImagesByHot, getImagesByTop


CACHE_DIR = os.path.join(xdg.XDG_CACHE_HOME,'pydit')
#CACHE_DIR = '/home/gcs/.cache/pydit/'

def printHelp():
    print("Usage: "+sys.argv[0]+" <subreddit> <mode> <limit>\n"+
            "subreddit: the name of the subreddit that you want to get the images without the r/\n"+
            "mode: new top hot\n"
            "limit: limit how many posts to download\n"
            )

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
    print("Looks like "+CACHE_DIR+" don't exist, creating it now.")
    os.mkdir(CACHE_DIR)

def main():
    print("Gabbie's reddit image downloader")
    if not directoryExists(CACHE_DIR):
        setup()
    if not directoryIsEmpty(CACHE_DIR):
        cleanDirectory(CACHE_DIR)
    if len(sys.argv) < 4:
        printHelp()
        exit()
    if sys.argv[2].lower() == "new":
        getImagesByNew(sys.argv[1],int(sys.argv[3]),CACHE_DIR)
    elif sys.argv[2].lower() == "hot":
        getImagesByHot(sys.argv[1],int(sys.argv[3]),CACHE_DIR)
    elif sys.argv[2].lower() == "top":
        getImagesByTop(sys.argv[1],int(sys.argv[3]),CACHE_DIR)
    if not directoryIsEmpty(CACHE_DIR):
        subprocess.run("sxiv -a "+'"'+CACHE_DIR+'/"*.*',shell=True)

if __name__ == '__main__':
    main()
