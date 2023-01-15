#!/bin/env python3
import os
from shutil import copy
from pydoc import doc
import subprocess
import configparser
import argparse
import urllib.request
import json
from pathlib import Path
from wsgiref import headers

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64; rv:101.0) Gecko/20100101 Firefox/101.0'
CACHE_DIR = os.path.join(os.environ['HOME'],'.cache','pydit')
CONFIG_DIR = os.path.join(os.environ['HOME'],'.config','pydit')
DOC_DIR = os.path.join(os.getenv('HOME'),'pydit')
PIC_DIR = os.path.join(os.getenv('HOME'),'pydit')
VID_DIR = os.path.join(os.getenv('HOME'),'pydit')

allowedextvid = [".mp4"]
allowedextimg = [".png",".jpg"]

def copyFiles(src:str,dest:str):
    for root, dirs, files in os.walk(src,topdown=True):
        for name in files:
            copy(os.path.join(src,name),os.path.join(dest,name))

def request_posts(subreddit:str,mode:str,limit:int):
    try:
        url = f'https://www.reddit.com/r/{subreddit}/{mode}.json?limit={limit}'
        req = urllib.request.Request(
            url, 
            data=None, 
            headers={
                'User-Agent': USER_AGENT
            }
        )
        return urllib.request.urlopen(req).read()
    except urllib.error.HTTPError as e:
        print(f'Error downloading the post list: {url}')
        print(e.__dict__)
        return None
    except urllib.error.URLError as e:
        print(f'Error downloading the post list: {url}')
        print(e.__dict__)
        return None

def download_file(url:str):
    try:
        req = urllib.request.Request(
                url, 
                data=None, 
                headers={
                    'User-Agent': USER_AGENT
                    }
                )
        return urllib.request.urlopen(req).read()
    except urllib.error.HTTPError as e:
        print(f'Error downloading file: {url}')
        print(e.__dict__)
        return None
    except urllib.error.URLError as e:
        print(f'Error downloading file: {url}')
        print(e.__dict__)
        return None
    
def getVideos(subreddit:str, mode:str, limit:int, destDir:str):
    # We try to get the JSON containing the posts from that subreddit 
    print(f'https://www.reddit.com/r/{subreddit}/{mode}.json?limit={limit}') 
    response = request_posts(subreddit,mode,limit)
    if response:
        jsonResponse = json.loads(response)
    else:
        exit()
    #then we iterate through until the limit of posts
    for post in jsonResponse['data']['children']:
        if not post['data']['is_video']: #all we care on this function is posts that are video
            continue
        filename = post['data']['media']['reddit_video']['fallback_url'].split('/')[4].split('?')[0] #get the full file name
        file_extension = os.path.splitext(filename)[1] #get the extension
        filename = filename.split('.')[0] #remove the extension from the full file name
        if file_extension in allowedextvid:
            #Downloading and saving the video
            print('Downloading video file '+post['data']['media']['reddit_video']['fallback_url'])
            video = download_file(post['data']['media']['reddit_video']['fallback_url'])
            with open(os.path.join(destDir,f'{filename}-video{file_extension}'),"wb") as outfile:
                outfile.write(video)
            #Downloading and saving the audio
            print('Downloading audio file '+post['data']['media']['reddit_video']['fallback_url'])
            audio = download_file(f"{os.path.split(post['data']['media']['reddit_video']['fallback_url'])[0]}/DASH_audio.mp4")
            with open(os.path.join(destDir,f'{filename}-audio{file_extension}'),'wb') as outfile:
                outfile.write(audio)
            #Merging the audio and video into a destination file
            print('Merging audio and video file')
            try:
                tmp_video = os.path.join(destDir,f'{filename}-video{file_extension}')
                tmp_audio = os.path.join(destDir,f'{filename}-audio{file_extension}')
                merged_file = os.path.join(destDir,f'{filename}{file_extension}')
                encoding = subprocess.check_output(f"ffmpeg -i {tmp_video} -i {tmp_audio} -c:v copy -c:a copy {merged_file}",shell=True)
            except subprocess.CalledProcessError as e:
                print(e.__dict__)
            #Removing the temporary audio and video files
            print('Removing the temporary audio and video files')
            os.remove(os.path.join(destDir,f'{filename}-audio{file_extension}'))
            os.remove(os.path.join(destDir,f'{filename}-video{file_extension}'))

def getImages(subreddit, mode, limit, destDir):
    #Downloading the post list json
    response = request_posts(subreddit,mode,limit)
    if response:
        jsonResponse = json.loads(response)
    else:
        exit()
    for post in jsonResponse['data']['children']:
        filename = post['data']['url'].split('/')[-1] 
        if os.path.splitext(filename)[-1] in allowedextimg:
            print('Downloading '+post['data']['url'])
            img = download_file(post['data']['url'])
            with open(os.path.join(destDir,filename),"wb") as outfile:
                outfile.write(img)

def getPosts(subreddit, mode, limit, destDir):
    print("https://www.reddit.com/r/"+subreddit+"/"+mode+".json?limit="+str(limit))
    response = request_posts(subreddit,mode,limit)
    if response:
        jsonResponse = json.loads(response)
    else:
        exit()
    with open(os.path.join(destDir,'posts.txt'),'w') as filp:
        for post in jsonResponse['data']['children']:
            filp.write('_________________________________________________\n')
            filp.write(f"{post['data']['title']} by {post['data']['author']}\n")
            filp.write(f"{post['data']['selftext']}\n")
            filp.write('_________________________________________________\n')

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
    try:
        global PIC_DIR
        global DOC_DIR
        global VID_DIR
        print("Checking for the existence of the cache directory")
        if not directoryExists(CACHE_DIR):
            print("Cache directory doesn't exist, creating now")
            os.mkdir(CACHE_DIR)
        print("Checking for the existence of the config directory")
        if not directoryExists(CONFIG_DIR):
            print("Config directory doesn't exist, creating now")
            os.mkdir(CONFIG_DIR)
        PIC_DIR = input(f"Enter your Pictures directory(default: {PIC_DIR}):")
        if not directoryExists(PIC_DIR):
            os.mkdir(os.path.join(PIC_DIR),'pydit')
        VID_DIR = input(f"Enter your Videos directory(default: {VID_DIR}):")
        if not directoryExists(VID_DIR):
            os.mkdir(os.path.join(VID_DIR),'pydit') 
        DOC_DIR = input(f"Enter your Documents directory(default: {DOC_DIR}):")
        if not directoryExists(DOC_DIR):
            os.mkdir(os.path.join(DOC_DIR),'pydit')
        with open(os.path.join(CONFIG_DIR,'config.txt'),'w') as filp:
            config = configparser.ConfigParser()
            config['PATHS'] = {
                'DOC_DIR': os.path.join(DOC_DIR,'pydit'),
                'PIC_DIR': os.path.join(PIC_DIR,'pydit'),
                'VID_DIR': os.path.join(VID_DIR,'pydit')

            }
            config.write(filp)   
        with open(os.path.join(CONFIG_DIR,'favorites.txt'),'w') as filp:
            filp.write('linuxmemes\n')
        print("Add your favorite subreddits on "+os.path.join(CONFIG_DIR,'favorites.txt'))
    except:
        print("Setup failed!")

def loadConfig():
    try:
        config = configparser.ConfigParser()
        config.read(os.path.join(CONFIG_DIR,'config.txt'))
        global PIC_DIR
        PIC_DIR = config['PATHS']['PIC_DIR']
        global DOC_DIR
        DOC_DIR = config['PATHS']['DOC_DIR']
        global VID_DIR 
        VID_DIR = config['PATHS']['DOC_DIR']
        return True
    except:
        return False

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
    print("Pydit - a reddit media scraper")
    # Parse the command-line arguments
    parser = argparse.ArgumentParser(description="A reddit media scraper")
    parser.add_argument('-s', '--subreddit', dest='subreddit', help='Subreddit to be scraped',type=str)
    parser.add_argument('-m', '--mode', dest='mode', help='Mode that the scraper will use, options: new, top, hot', required = True, type=str)
    parser.add_argument('-l', '--limit', dest='limit', help='How many posts will be downloaded',default=100, type=int)
    parser.add_argument('-f', '--favorite', action= 'store_true', dest='favorite', help='Choose option from favorite file',default=False)
    parser.add_argument('-t','--type',dest='mediatype',help='Media type to be downloaded, options:image ,video , text', type=str, default="image")
    parser.add_argument('-k', '--keep', action= 'store_true', dest='keepfiles', help='Keep the scraped files permanently',default=False)
    parser.add_argument('-n','--noexec', action= 'store_true', dest='noexec', help='Download only, will not execute any players/viewers',default=False)
    parser.add_argument('-r','--re-setup',action='store_true',dest='resetup',help='Force the setup process to happen again.',default=False)
    args= parser.parse_args()
    # Check if the required directories exist on XDG config and cache user dirs
    if (not directoryExists(CACHE_DIR)) or (not directoryExists(CONFIG_DIR)) or args.resetup:
        setup()
    if not loadConfig():
        print("Could not load the config file, try to run with the -r to redo the configuration.")
        exit()
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
