# pydit
## About the project
Reddit media downloader written in python

I made this project to make it easy to get to the interesting part of reddit without the unnecessary part that is the interface.

Also used to archive stuff from subreddits that i like, it also bypass the restriction for signing in to reddit to see NSFW stuff.

The project is currently feature complete, it download text posts, images and videos, but from now on i will do only bugfixes, if you managed to find any bug please report on the issues.
## Dependencies

`sxiv`: check your distro repository, quite common package should exist there.

`mpv`: check your distro repository, also quite common package should exist there too.
## Usage
usage: pydit.py [-h] [-s SUBREDDIT] -m MODE [-l LIMIT] [-f]

A reddit media scraper
```
  -s SUBREDDIT, --subreddit SUBREDDIT

                        Subreddit to be scraped

  -m MODE, --mode MODE  Mode that the scraper will use, options: new, top, hot

  -l LIMIT, --limit LIMIT

                        How many posts will be downloaded

  -f, --favorite        Choose option from favorite file

  -fc, --favorite-curses

                        Choose option from favorite file using a curses UI

  -t MEDIATYPE, --type MEDIATYPE

                        Media type to be downloaded, options:image ,video ,

                        text

  -k, --keep            Keep the scraped files permanently

  -n, --noexec          Download only, will not execute any players/viewers

  -r, --re-setup        Force the setup process to happen again.
```
