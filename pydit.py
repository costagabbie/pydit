#!/bin/env python3
import os
from shutil import copy
from pydoc import doc
import subprocess
import argparse
import urllib.request
import json
from pathlib import Path
from wsgiref import headers

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64; rv:101.0) Gecko/20100101 Firefox/101.0'
CACHE_DIR = os.path.join(os.environ['HOME'],'.cache','pydit')
CONFIG_DIR = os.path.join(os.environ['HOME'],'.config','pydit')
DOC_DIR = os.path.join(os.environ['HOME'],'Documents','pydit')
PIC_DIR = os.path.join(os.environ['HOME'],'Pictures','pydit')
VID_DIR = os.path.join(os.environ['HOME'],'Videos','pydit')

allowedextvid = [".mp4"]
allowedextimg = [".png",".jpg"]



def copyFiles(src,dest):
    for root, dirs, files in os.walk(src,topdown=True):
        for name in files:
            copy(os.path.join(src,name),os.path.join(dest,name))

def getVideos(subreddit, mode, limit, destDir):
    try:
        print("https://www.reddit.com/r/"+subreddit+"/"+mode+".json?limit="+str(limit))
        req = urllib.request.Request(
            "https://www.reddit.com/r/"+subreddit+"/"+mode+".json?limit="+str(limit), 
            data=None, 
            headers={
                'User-Agent': USER_AGENT
            }
        )
        response = urllib.request.urlopen(req).read() #urllib.request.urlopen("https://www.reddit.com/r/"+subreddit+"/"+mode+".json?limit="+str(limit)).read()
        jsonResponse = json.loads(response)
    except urllib.error.HTTPError as e:
        print("Error downloading the image :"+jsonResponse['data']['children'][i]['data']['url'])
        print(e.__dict__)
    except urllib.error.URLError as e:
        print("Error downloading the image :"+jsonResponse['data']['children'][i]['data']['url'])
        print(e.__dict__)
    for i in range(limit):
        if not jsonResponse['data']['children'][i]['data']['is_video']:
            continue
        filename = jsonResponse['data']['children'][i]['data']['media']['reddit_video']['scrubber_media_url'].split('/')[-1] 
        if os.path.splitext(filename)[-1] in allowedextvid:
            try:
                print('Downloading '+jsonResponse['data']['children'][i]['data']['media']['reddit_video']['scrubber_media_url'])
                req = urllib.request.Request(
                jsonResponse['data']['children'][i]['data']['media']['reddit_video']['scrubber_media_url'], 
                data=None, 
                headers={
                    'User-Agent': USER_AGENT
                    }
                )
                img = urllib.request.urlopen(req).read()#img = urllib.request.urlopen(jsonResponse['data']['children'][i]['data']['media']['reddit_video']['scrubber_media_url'], headers={'User-Agent': USER_AGENT}).read()
                with open(os.path.join(destDir,filename),"wb") as outfile:
                    outfile.write(img)
            except urllib.error.HTTPError as e:
                print("Error downloading the video :"+jsonResponse['data']['children'][i]['data']['media']['reddit_video']['scrubber_media_url'])
                print(e.__dict__)
            except urllib.error.URLError as e:
                print("Error downloading the video :"+jsonResponse['data']['children'][i]['data']['media']['reddit_video']['scrubber_media_url'])
                print(e.__dict__)
                

def getImages(subreddit, mode, limit, destDir):
    try:
        print("https://www.reddit.com/r/"+subreddit+"/"+mode+".json?limit="+str(limit))
        req = urllib.request.Request(
            "https://www.reddit.com/r/"+subreddit+"/"+mode+".json?limit="+str(limit), 
            data=None, 
            headers={
                'User-Agent': USER_AGENT
            }
        )
        response = urllib.request.urlopen(req).read()
        jsonResponse = json.loads(response)
    except urllib.error.HTTPError as ex:
        print("Error getting the image list:")
        exit()
    for i in range(limit):
        filename = jsonResponse['data']['children'][i]['data']['url'].split('/')[-1] 
        if os.path.splitext(filename)[-1] in allowedextimg:
            try:
                print('Downloading '+jsonResponse['data']['children'][i]['data']['url'])
                req = urllib.request.Request(
                jsonResponse['data']['children'][i]['data']['url'], 
                data=None, 
                headers={
                    'User-Agent': USER_AGENT
                    }
                )
                img = urllib.request.urlopen(req).read()
                with open(os.path.join(destDir,filename),"wb") as outfile:
                    outfile.write(img)
            except urllib.error.HTTPError as e:
                print("Error downloading the image :"+jsonResponse['data']['children'][i]['data']['url'])
                print(e.__dict__)
            except urllib.error.URLError as e:
                print("Error downloading the image :"+jsonResponse['data']['children'][i]['data']['url'])
                print(e.__dict__)
def getPosts(subreddit, mode, limit, destDir):
    try:
        print("https://www.reddit.com/r/"+subreddit+"/"+mode+".json?limit="+str(limit))
        req = urllib.request.Request(
            "https://www.reddit.com/r/"+subreddit+"/"+mode+".json?limit="+str(limit), 
            data=None, 
            headers={
                'User-Agent': USER_AGENT
            }
        )
        response = urllib.request.urlopen(req).read()
        jsonResponse = json.loads(response)
    except urllib.error.HTTPError as e:
        print("Error getting the post list:")
        print(e.__dict__)
    except urllib.error.URLError as e:
        print("Error getting the post list:")
        print(e.__dict__)
        exit()
    with open(os.path.join(destDir,'posts.txt'),'w') as filp:
        for i in range(limit):
            post = jsonResponse['data']['children'][i]['data']['selftext']
            title = jsonResponse['data']['children'][i]['data']['title']
            author = jsonResponse['data']['children'][i]['data']['author']
            filp.write("_________________________________________________\n")
            filp.write(title+" by "+author+"\n")
            filp.write(post+"\n")
            filp.write("_________________________________________________\n")

def saveCache(mediaType, subreddit):
    if mediaType == "text":
        #Check if the destination folder exist
        if not directoryExists(os.path.join(DOC_DIR,subreddit)):
            os.mkdir(os.path.join(DOC_DIR,subreddit))
        #Copy file from the cache to the Documents/subreddit dir
        copyFiles(CACHE_DIR,os.path.join(DOC_DIR,subreddit))
        print("pydit cache permanently saved at: "+os.path.join(DOC_DIR,subreddit))    
    elif mediaType == "image":
        #Check if the destination folder exist
        if not directoryExists(os.path.join(PIC_DIR,subreddit)):
            os.mkdir(os.path.join(PIC_DIR,subreddit))
        #Copy file from the cache to the Pictures/subreddit dir
        copyFiles(CACHE_DIR,os.path.join(PIC_DIR,subreddit))
        print("pydit cache permanently saved at: "+os.path.join(PIC_DIR,subreddit))
    elif mediaType == "video":
        #Check if the destination folder exist
        if not directoryExists(os.path.join(VID_DIR,subreddit)):
            os.mkdir(os.path.join(VID_DIR,subreddit))
        #Copy file from the cache to the Videos/subreddit dir
        copyFiles(CACHE_DIR,os.path.join(VID_DIR,subreddit))
        print("pydit cache permanently saved at: "+os.path.join(VID_DIR,subreddit))

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
    os.mkdir(PIC_DIR)
    os.mkdir(DOC_DIR)
    os.mkdir(VID_DIR)
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
    print("Reddit media scraper")
    # Parse the command-line arguments
    parser = argparse.ArgumentParser(description="A reddit media scraper")
    parser.add_argument('-s', '--subreddit', dest='subreddit', help='Subreddit to be scraped',type=str)
    parser.add_argument('-m', '--mode', dest='mode', help='Mode that the scraper will use, options: new, top, hot', required = True, type=str)
    parser.add_argument('-l', '--limit', dest='limit', help='How many posts will be downloaded',default=100, type=int)
    parser.add_argument('-f', '--favorite', action= 'store_true', dest='favorite', help='Choose option from favorite file',default=False)
    parser.add_argument('-t','--type',dest='mediatype',help='Media type to be downloaded, options:image ,video , text', type=str, default="image")
    parser.add_argument('-k', '--keep', action= 'store_true', dest='keepfiles', help='Keep the scraped files permanently',default=False)
    parser.add_argument('-n','--noexec', action= 'store_true', dest='noexec', help='Download only, will not execute any players/viewers',default=False)
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
    # Check the media type that we want
    if args.mediatype == 'image':
        # Check the mode that we want
        if args.mode.lower() in ["new","top","hot"]:
            getImages(sub,args.mode.lower(),int(args.limit), CACHE_DIR)
        #Check if there is some image to display
        if (not directoryIsEmpty(CACHE_DIR)) and (not args.noexec):
            subprocess.run("sxiv -a "+'"'+CACHE_DIR+'/"*.*',shell=True)
    elif args.mediatype == 'video':
        if args.mode.lower() in ["new","top","hot"]:
            getVideos(sub,args.mode.lower(),int(args.limit), CACHE_DIR)
        #Check if there is some image to display
        if (not directoryIsEmpty(CACHE_DIR)) and (not args.noexec):
            for file in os.listdir(CACHE_DIR):
                subprocess.run("mpv "+'"'+CACHE_DIR+'/'+file+'"',shell=True)
                x = input("What to do next? [N]ext [Q]uit?: ")
                if x == 'q':
                    break
    elif args.mediatype == 'text':
        if args.mode.lower() in ["new","top","hot"]:
            getPosts(sub,args.mode.lower(),int(args.limit), CACHE_DIR)
        if (not directoryIsEmpty(CACHE_DIR)) and (not args.noexec):
            subprocess.run("less "+'"'+CACHE_DIR+'/posts.txt"',shell=True)
    #Check if we want to keep
    if args.keepfiles :
        saveCache(args.mediatype,sub)

# Setting the "entrypoint" of the script      
if __name__ == '__main__':
    main()
