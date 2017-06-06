import datetime
import hashlib
import os
import random
import sys

import requests
from bs4 import BeautifulSoup
from pprint import pprint as pp
from collections import defaultdict
from operator import itemgetter
from dateutil import parser as dtparser


START_YEAR = 2000
END_YEAR = 2018
RAW_DATA_DIR = 'wikixml'


def file_exists(fname):
    if os.path.isfile(fname):
        return True
    return False

def write_text(data, f_path):
        with open(f_path, 'w') as outfile:
            outfile.write(data)
        print('{} written.').format(f_path)

def read_text(f_path):
    with open (f_path, "r") as infile:
        txt=infile.read()
    print('Read {}.'.format(f_path))
    return txt

def get_resource(url):
        print('Fetching: {}'.format(url))
        r = requests.get(url)
        if r.status_code != 200:
            print('Error: {}.'.format(r.status_code))
        return r

class WikiEdits:
    def __init__(self, data_dir='wikixml'):
        self.base_url = 'https://en.wikipedia.org/wiki/Special:Export/'
        self.data_dir = data_dir
        print self.data_dir
    def get_history(self, title):
        dstfile = '{}/{}.xml'.format(self.data_dir, title.lower())
        url = '{}{}?history'.format(self.base_url, title)
        r = get_resource(url)
        write_text(r.content, dstfile)

    def extract_article_text(self, s, title):
        title = title.lower()
        title = title.replace('_', ' ')
        s = s.lower()
        parts = s.split(title)
        s = title.join(parts[1:-1])
        s = title + s
        lines = s.splitlines()
        result = []
        for line in lines:
            line = line.strip()
            if line:
                result.append(line)
        return result
    #def parse(self, title, refresh=False, y_scale=1.0):

