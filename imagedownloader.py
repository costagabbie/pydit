import json
import os
import urllib.request
allowedext = [".png",".jpg"]

def getImagesByNew(subreddit, limit, destDir):
    try:
        print("https://www.reddit.com/r/"+subreddit+"/new.json?limit="+str(limit))
        response = urllib.request.urlopen("https://www.reddit.com/r/"+subreddit+"/hot.json?limit="+str(limit)).read()
        jsonResponse = json.loads(response)
    except:
        print("Error getting the image list.")
        exit()
    for i in range(limit):
        filename = jsonResponse['data']['children'][i]['data']['url'].split('/')[-1] 
        if os.path.splitext(filename)[-1] in allowedext:
            try:
                print('Downloading '+jsonResponse['data']['children'][i]['data']['url'])
                img = urllib.request.urlopen(jsonResponse['data']['children'][i]['data']['url']).read()
                with open(os.path.join(destDir,filename),"wb") as outfile:
                    outfile.write(img)
            except:
                print("Error downloading the image :"+jsonResponse['data']['children'][i]['data']['url'])


def getImagesByHot(subreddit, limit, destDir):
    try:
        print("https://www.reddit.com/r/"+subreddit+"/hot.json?limit="+str(limit))
        response = urllib.request.urlopen("https://www.reddit.com/r/"+subreddit+"/hot.json?limit="+str(limit)).read()
        jsonResponse = json.loads(response)
    except:
        print("Error getting the image list.")
        exit()
    for i in range(limit):
        filename = jsonResponse['data']['children'][i]['data']['url'].split('/')[-1] 
        if os.path.splitext(filename)[-1] in allowedext:
            try:
                print('Downloading '+jsonResponse['data']['children'][i]['data']['url'])
                img = urllib.request.urlopen(jsonResponse['data']['children'][i]['data']['url']).read()
                with open(os.path.join(destDir,filename),"wb") as outfile:
                    outfile.write(img)
            except:
                print("Error downloading the image :"+jsonResponse['data']['children'][i]['data']['url'])


def getImagesByTop(subreddit, limit, destDir):
    try:
        print("https://www.reddit.com/r/"+subreddit+"/top.json?limit="+str(limit))
        response = urllib.request.urlopen("https://www.reddit.com/r/"+subreddit+"/hot.json?limit="+str(limit)).read()
        jsonResponse = json.loads(response)
    except:
        print("Error getting the image list.")
        exit()
    for i in range(limit):
        filename = jsonResponse['data']['children'][i]['data']['url'].split('/')[-1] 
        if os.path.splitext(filename)[-1] in allowedext:
            try:
                print('Downloading '+jsonResponse['data']['children'][i]['data']['url'])
                img = urllib.request.urlopen(jsonResponse['data']['children'][i]['data']['url']).read()
                with open(os.path.join(destDir,filename),"wb") as outfile:
                    outfile.write(img)
            except:
                print("Error downloading the image :"+jsonResponse['data']['children'][i]['data']['url'])