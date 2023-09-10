#!/bin/env python3
import argparse
import configparser
import curses
import json
import os
import subprocess
import urllib.request
from pathlib import Path
from shutil import copy

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:101.0) Gecko/20100101 Firefox/101.0"
CACHE_DIR = os.path.join(os.environ["HOME"], ".cache", "pydit")
CONFIG_DIR = os.path.join(os.environ["HOME"], ".config", "pydit")
DOC_DIR = os.path.join(os.getenv("HOME"), "pydit")
PIC_DIR = os.path.join(os.getenv("HOME"), "pydit")
VID_DIR = os.path.join(os.getenv("HOME"), "pydit")
ALLOWED_VID_EXTENSIONS = [".mp4"]
ALLOWED_IMG_EXTENSIONS = [".png", ".jpg"]

curses_subreddit = ""

def copy_files(src: str, dest: str):
    for root, dirs, files in os.walk(src, topdown=True):
        for name in files:
            copy(os.path.join(src, name), os.path.join(dest, name))


def request_posts(subreddit: str, mode: str, limit: int):
    try:
        url = f"https://www.reddit.com/r/{subreddit}/{mode}.json?limit={limit}".replace(
            " ", "%20"
        )
        req = urllib.request.Request(url, data=None, headers={"User-Agent": USER_AGENT})
        return urllib.request.urlopen(req).read()
    except urllib.error.HTTPError as e:
        print(f"Error downloading the post list: {url}")
        print(e.__dict__)
        return None
    except urllib.error.URLError as e:
        print(f"Error downloading the post list: {url}")
        print(e.__dict__)
        return None

def download_file(url: str):
    try:
        req = urllib.request.Request(url, data=None, headers={"User-Agent": USER_AGENT})
        return urllib.request.urlopen(req).read()
    except urllib.error.HTTPError as e:
        print(f"Error downloading file: {url}")
        print(e.__dict__)
        return None
    except urllib.error.URLError as e:
        print(f"Error downloading file: {url}")
        print(e.__dict__)
        return None

def get_videos(subreddit: str, mode: str, limit: int, destination_dir: str):
    # We try to get the JSON containing the posts from that subreddit
    print(f"https://www.reddit.com/r/{subreddit}/{mode}.json?limit={limit}")
    response = request_posts(subreddit, mode, limit)
    if response:
        json_response = json.loads(response)
    else:
        exit()
    # then we iterate through until the limit of posts
    for post in json_response["data"]["children"]:
        if not post["data"][
            "is_video"
        ]:  # all we care on this function is posts that are video
            continue
        filename = (
            post["data"]["media"]["reddit_video"]["fallback_url"]
            .split("/")[4]
            .split("?")[0]
        )  # get the full file name
        file_extension = os.path.splitext(filename)[1]  # get the extension
        filename = filename.split(".")[
            0
        ]  # remove the extension from the full file name
        tmp_video = os.path.join(destination_dir, f"{filename}-video{file_extension}")
        tmp_audio = os.path.join(destination_dir, f"{filename}-audio{file_extension}")
        merged_file = os.path.join(
            destination_dir,
            f"{post['data']['media']['reddit_video']['fallback_url'].split('/')[3]}{file_extension}",
        )
        if file_extension in ALLOWED_VID_EXTENSIONS:
            # Downloading and saving the video
            print(
                f"Downloading video file {post['data']['media']['reddit_video']['fallback_url']}"
            )
            video = download_file(post["data"]["media"]["reddit_video"]["fallback_url"])
            if video:
                with open(
                    os.path.join(destination_dir, f"{filename}-video{file_extension}"),
                    "wb",
                ) as output_file:
                    output_file.write(video)
            else:
                continue
            # Downloading and saving the audio
            print(
                f"Downloading audio file {post['data']['media']['reddit_video']['fallback_url']}"
            )
            audio = download_file(
                f"{os.path.split(post['data']['media']['reddit_video']['fallback_url'])[0]}/DASH_audio.mp4"
            )
            if audio:
                with open(
                    os.path.join(destination_dir, f"{filename}-audio{file_extension}"),
                    "wb",
                ) as output_file:
                    output_file.write(audio)
            else:
                os.remove(tmp_video)
                continue
            # Merging the audio and video into a destination file
            print("Merging audio and video file")
            try:
                encoding = subprocess.check_output(
                    f"ffmpeg -i {tmp_video} -i {tmp_audio} -c:v copy -c:a copy {merged_file}",
                    shell=True,
                )
            except subprocess.CalledProcessError as e:
                print(e.__dict__)
            # Removing the temporary audio and video files
            print("Removing the temporary audio and video files")
            os.remove(tmp_audio)
            os.remove(tmp_video)

def get_images(subreddit, mode, limit, destination_dir):
    # Downloading the post list json
    response = request_posts(subreddit, mode, limit)
    if response:
        json_response = json.loads(response)
    else:
        exit()
    for post in json_response["data"]["children"]:
        filename = post["data"]["url"].split("/")[-1]
        if os.path.splitext(filename)[-1] in ALLOWED_IMG_EXTENSIONS:
            print(f"Downloading  + {post['data']['url']}")
            img = download_file(post["data"]["url"])
            if img:
                with open(os.path.join(destination_dir, filename), "wb") as output_file:
                    output_file.write(img)
            else:
                continue

def get_posts(subreddit: str, mode: str, limit: int, destination_dir: str):
    print(f"https://www.reddit.com/r/{subreddit}/{mode}.json?limit={limit}")
    response = request_posts(subreddit, mode, limit)
    if response:
        json_response = json.loads(response)
    else:
        exit()
    with open(os.path.join(destination_dir, "posts.txt"), "w") as favorite_file:
        for post in json_response["data"]["children"]:
            favorite_file.write("_________________________________________________\n")
            favorite_file.write(
                f"{post['data']['title']} by {post['data']['author']}\n"
            )
            favorite_file.write(f"{post['data']['selftext']}\n")
            favorite_file.write("_________________________________________________\n")

def save_cache(media_type: str, subreddit: str):
    if media_type == "text":
        # Check if the destination folder exist
        if not directory_exists(os.path.join(DOC_DIR, subreddit)):
            os.mkdir(os.path.join(DOC_DIR, subreddit))
        # Copy file from the cache to the Documents/subreddit dir
        copy_files(CACHE_DIR, os.path.join(DOC_DIR, subreddit))
        print("pydit cache permanently saved at: " + os.path.join(DOC_DIR, subreddit))
    elif media_type == "image":
        # Check if the destination folder exist
        if not directory_exists(os.path.join(PIC_DIR, subreddit)):
            os.mkdir(os.path.join(PIC_DIR, subreddit))
        # Copy file from the cache to the Pictures/subreddit dir
        copy_files(CACHE_DIR, os.path.join(PIC_DIR, subreddit))
        print("pydit cache permanently saved at: " + os.path.join(PIC_DIR, subreddit))
    elif media_type == "video":
        # Check if the destination folder exist
        if not directory_exists(os.path.join(VID_DIR, subreddit)):
            os.mkdir(os.path.join(VID_DIR, subreddit))
        # Copy file from the cache to the Videos/subreddit dir
        copy_files(CACHE_DIR, os.path.join(VID_DIR, subreddit))
        print("pydit cache permanently saved at: " + os.path.join(VID_DIR, subreddit))

def directory_exists(dirname):
    d = Path(dirname)
    return d.exists() and d.is_dir()

def directory_is_empty(path):
    return len(os.listdir(path)) == 0

def clean_directory(path):
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
        if not directory_exists(CACHE_DIR):
            print("Cache directory doesn't exist, creating now")
            os.mkdir(CACHE_DIR)
        print("Checking for the existence of the config directory")
        if not directory_exists(CONFIG_DIR):
            print("Config directory doesn't exist, creating now")
            os.mkdir(CONFIG_DIR)
        PIC_DIR = input(f"Enter your Pictures directory(default: {PIC_DIR}):")
        if not directory_exists(PIC_DIR):
            os.mkdir(os.path.join(PIC_DIR), "pydit")
        VID_DIR = input(f"Enter your Videos directory(default: {VID_DIR}):")
        if not directory_exists(VID_DIR):
            os.mkdir(os.path.join(VID_DIR), "pydit")
        DOC_DIR = input(f"Enter your Documents directory(default: {DOC_DIR}):")
        if not directory_exists(DOC_DIR):
            os.mkdir(os.path.join(DOC_DIR), "pydit")
        with open(os.path.join(CONFIG_DIR, "config.txt"), "w") as favorite_file:
            config = configparser.ConfigParser()
            config["PATHS"] = {
                "DOC_DIR": os.path.join(DOC_DIR, "pydit"),
                "PIC_DIR": os.path.join(PIC_DIR, "pydit"),
                "VID_DIR": os.path.join(VID_DIR, "pydit"),
            }
            config.write(favorite_file)
        with open(os.path.join(CONFIG_DIR, "favorites.txt"), "w") as favorite_file:
            favorite_file.write("linuxmemes\n")
        print(
            "Add your favorite subreddits on "
            + os.path.join(CONFIG_DIR, "favorites.txt")
        )
    except:
        print("Setup failed!")

def load_config():
    try:
        config = configparser.ConfigParser()
        config.read(os.path.join(CONFIG_DIR, "config.txt"))
        global PIC_DIR
        PIC_DIR = config["PATHS"]["PIC_DIR"]
        global DOC_DIR
        DOC_DIR = config["PATHS"]["DOC_DIR"]
        global VID_DIR
        VID_DIR = config["PATHS"]["VID_DIR"]
        return True
    except:
        return False

def update_curses_picker(
    scr: curses.window, pad: curses.window, items: list, item_index: int
):
    scr.clrtobot()
    pad.clrtobot()
    scr.addstr(1, 1, "Pydit - a reddit media scraper", curses.A_BOLD)
    scr.addstr(2, 1, "Please pick your favorite:")
    i = 0
    for item in items:
        pad.clrtoeol()
        if i == item_index:
            pad.addstr(i, 0, item, curses.color_pair(1))
        else:
            pad.addstr(i, 0, item)
        i += 1

def curses_favorite_picker(arg):
    global curses_subreddit
    selected_item = 0
    favorites = []
    scr = curses.initscr()
    scr.keypad(True)
    curses.curs_set(0)
    curses.noecho()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    i = 0
    with open(os.path.join(CONFIG_DIR, "favorites.txt"), "r") as favorite_file:
        for line in favorite_file:
            if line[-1] == "\n":
                favorites.append(line[:-1])
            else:
                favorites.append(line)
            i = i + 1
    pad = curses.newpad(len(favorites), curses.COLS - 1)
    update_curses_picker(scr, pad, favorites, selected_item)
    scr.refresh()
    pad.refresh(0, 0, 3, 1, curses.LINES - 1, curses.COLS - 2)
    curses_subreddit = favorites[selected_item]
    while True:
        key_pressed = scr.getch()
        if key_pressed in [curses.KEY_ENTER, 13, 10]:
            break
        elif key_pressed == curses.KEY_UP:
            if selected_item > 0:
                selected_item -= 1
                curses_subreddit = favorites[selected_item]
                update_curses_picker(scr, pad, favorites, selected_item)
                scr.refresh()
                if selected_item <= curses.LINES - 2:
                    pad.refresh(0, 0, 3, 1, curses.LINES - 1, curses.COLS - 1)
                else:
                    pad.refresh(
                        selected_item, 0, 3, 1, curses.LINES - 1, curses.COLS - 1
                    )
        elif key_pressed == curses.KEY_DOWN:
            if selected_item < len(favorites) - 1:
                selected_item += 1
                curses_subreddit = favorites[selected_item]
                update_curses_picker(scr, pad, favorites, selected_item)
                scr.refresh()
                if selected_item <= curses.LINES - 5:
                    pad.refresh(0, 0, 3, 1, curses.LINES - 1, curses.COLS - 1)
                else:
                    pad.refresh(
                        selected_item, 0, 3, 1, curses.LINES - 1, curses.COLS - 1
                    )

def get_sub_from_favorites():
    subreddits = []
    i = 1
    with open(os.path.join(CONFIG_DIR, "favorites.txt"), "r") as favorite_file:
        for line in favorite_file:
            print(f"[{i}] - {line}")
            if line[-1] == "\n":
                subreddits.append(line[:-1])
            else:
                subreddits.append(line)
            i = i + 1
    subreddit = int(input("Please select the subreddit number, or zero to quit:"))
    if subreddit == 0:
        exit()
    return subreddits[subreddit - 1]

def get_all_favorites():
    subreddits = []
    with open(os.path.join(CONFIG_DIR, "favorites.txt"), "r") as favorite_file:
        for line in favorite_file:
            if line[-1] == "\n":
                subreddits.append(line[:-1])
            else:
                subreddits.append(line)
    return subreddits

def main():
    # Script title
    print("Pydit - a reddit media scraper")
    # Parse the command-line arguments
    parser = argparse.ArgumentParser(description="A reddit media scraper")
    parser.add_argument(
        "-s", "--subreddit", dest="subreddit", help="Subreddit to be scraped", type=str
    )
    parser.add_argument(
        "-m",
        "--mode",
        dest="mode",
        help="Mode that the scraper will use, options: new, top, hot",
        required=True,
        type=str,
    )
    parser.add_argument(
        "-l",
        "--limit",
        dest="limit",
        help="How many posts will be downloaded",
        default=100,
        type=int,
    )
    parser.add_argument(
        "-f",
        "--favorite",
        action="store_true",
        dest="favorite",
        help="Choose option from favorite file",
        default=False,
    )
    parser.add_argument(
        "-fc",
        "--favorite-curses",
        action="store_true",
        dest="favoritecurses",
        help="Choose option from favorite file using a curses UI",
        default=False,
    )
    parser.add_argument(
        "-t",
        "--type",
        dest="media_type",
        help="Media type to be downloaded, options:image ,video , text",
        type=str,
        default="image",
    )
    parser.add_argument(
        "-k",
        "--keep",
        action="store_true",
        dest="keepfiles",
        help="Keep the scraped files permanently",
        default=False,
    )
    parser.add_argument(
        "-n",
        "--noexec",
        action="store_true",
        dest="noexec",
        help="Download only, will not execute any players/viewers",
        default=False,
    )
    parser.add_argument(
        "-r",
        "--re-setup",
        action="store_true",
        dest="resetup",
        help="Force the setup process to happen again.",
        default=False,
    )
    parser.add_argument(
        "-a",
        "-all",
        action="store_true",
        dest="downloadall",
        help="Download from all favorites ",
    )
    args = parser.parse_args()
    # Check if the required directories exist on XDG config and cache user dirs
    if (
        (not directory_exists(CACHE_DIR))
        or (not directory_exists(CONFIG_DIR))
        or args.resetup
    ):
        setup()
    if not load_config():
        print(
            "Could not load the config file, try to run with the -r to redo the configuration."
        )
        exit()
    # Check if the cache directory is empty, so we don't display repeated content from other runs
    if not directory_is_empty(CACHE_DIR):
        clean_directory(CACHE_DIR)
    # Check if we are downloading everything on our favorite list
    if args.downloadall:
        if args.media_type == "image":
            subs = get_all_favorites()
            for subreddit in subs:
                get_images(subreddit, args.mode.lower(), args.limit, CACHE_DIR)
                save_cache(args.media_type, subreddit)
                clean_directory(CACHE_DIR)
        if args.media_type == "video":
            subs = get_all_favorites()
            for subreddit in subs:
                print(f"Downloading from {subreddit}")
                get_videos(subreddit, args.mode.lower(), args.limit, CACHE_DIR)
                save_cache(args.media_type, subreddit)
                clean_directory(CACHE_DIR)

    # Check if we are using the favorite subreddit list
    if args.favorite:
        sub = get_sub_from_favorites()
    elif (
        args.favoritecurses
    ):  # Or if we want to use our fancy new curses based ui to pick favorites
        curses.wrapper(curses_favorite_picker)
        curses.reset_shell_mode()
        if curses_subreddit != "":
            sub = curses_subreddit
        else:
            sub = ""
    else:  # or if we want to get the subreddit from the command line argument
        sub = args.subreddit

    if sub == "":
        print("No subreddit specified, quitting now.")
        exit()
    # Check the media type that we want
    if args.media_type == "image":
        # Check the mode that we want
        if args.mode.lower() in ["new", "top", "hot"]:
            get_images(sub, args.mode.lower(), int(args.limit), CACHE_DIR)
        # Check if there is some image to display
        if (not directory_is_empty(CACHE_DIR)) and (not args.noexec):
            subprocess.run("sxiv -a " + '"' + CACHE_DIR + '/"*.*', shell=True)
    elif args.media_type == "video":
        if args.mode.lower() in ["new", "top", "hot"]:
            get_videos(sub, args.mode.lower(), int(args.limit), CACHE_DIR)
        # Check if there is some image to display
        if (not directory_is_empty(CACHE_DIR)) and (not args.noexec):
            for file in os.listdir(CACHE_DIR):
                subprocess.run("mpv " + '"' + CACHE_DIR + "/" + file + '"', shell=True)
                x = input("What to do next? [N]ext [Q]uit?: ")
                if x == "q":
                    break
    elif args.media_type == "text":
        if args.mode.lower() in ["new", "top", "hot"]:
            get_posts(sub, args.mode.lower(), int(args.limit), CACHE_DIR)
        if (not directory_is_empty(CACHE_DIR)) and (not args.noexec):
            subprocess.run("less " + '"' + CACHE_DIR + '/posts.txt"', shell=True)
    # Check if we want to keep
    if args.keepfiles:
        save_cache(args.media_type, sub)

# Setting the "entrypoint" of the script
if __name__ == "__main__":
    main()
