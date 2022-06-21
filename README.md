# pydit
Reddit media downloader written in python
# Dependencies

`sxiv`: check your distro repository, quite common package should exist there.

`mpv`: check your distro repository, also quite common package should exist there too.
# Usage
usage: pydit.py [-h] [-s SUBREDDIT] -m MODE [-l LIMIT] [-f]

A reddit media scraper

optional arguments:

  -h, --help            show this help message and exit
  
  -s SUBREDDIT, --subreddit SUBREDDIT Subreddit to be scraped
  
  -m MODE, --mode MODE  Mode that the scraper will use, options: new, top, hot
  
  -l LIMIT, --limit LIMIT How many posts will be downloaded
  
  -f, --favorite        Choose option from favorite file
  
  -t MEDIATYPE, --type MEDIATYPE Media type to be downloaded, options:image ,video , text
  
  -k, --keep            Keep the scraped files permanently
