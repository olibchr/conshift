import os
import sys, csv
import requests
from bs4 import BeautifulSoup
from dateutil import parser as dtparser
import pytz

START_YEAR = 2000
END_YEAR = 2018
RAW_DATA_DIR = 'wikixml'
if len(sys.argv) > 1: CONCEPT = sys.argv[1]
else: CONCEPT = 'Uber_(company)'
STARTDATE = dtparser.parse('2014-08-13T00:00:00Z')
ENDDATE = dtparser.parse('2015-08-14T00:00:00Z')

utc = pytz.UTC
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
        print "Resource obtained"
        if r.status_code != 200:
            print('Error: {}.'.format(r.status_code))
        return r

class WikiEdits:
    def __init__(self, data_dir='wikixml'):
        self.base_url = 'https://en.wikipedia.org/wiki/Special:Export/'
        self.data_dir = data_dir
        print self.data_dir
    def get_history(self, title):
        url = '{}{}?history'.format(self.base_url, title)
        r = get_resource(url)
        return r.content

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
    def parse(self, title, refresh=False):
        self.revisions = []
        srcfile = '{}/{}.xml'.format(self.data_dir, title.lower())
        txt = self.get_history(title)
        #txt = read_text(srcfile)
        print 'Parsing ...'
        soup = BeautifulSoup(txt, 'lxml-xml')
        print 'Finding revisions ...'
        revisions = soup.find_all('revision')

        for i, rev in enumerate(revisions):
            row = {
                'id':rev.id.get_text(),
                'dt':dtparser.parse(rev.timestamp.get_text()),
                'change': abs(len(rev.text)-len(revisions[i-1].text))
            }
            if row['dt'] > ENDDATE: continue
            if row['dt'] < STARTDATE: continue
            self.revisions.append(dict(row))

    def split_revisions(self, intervals):
        self.revisions = sorted(self.revisions, key=lambda rev: rev['dt'])
        self.rev_in_timeframe = [[] for i in range(len(intervals))]
        self.rev_tf_sums = [0] * (len(intervals))
        if len(intervals) == 0: print "intervall error"; return
        i = 0
        for rev in self.revisions:
            if i >= len(intervals): print intervals
            while rev['dt'] > utc.localize(intervals[i]): i+= 1
            self.rev_in_timeframe[i].append(rev)
            self.rev_tf_sums[i] += 1
        self.rev_tf_sums = [self.rev_tf_sums[e] + self.rev_tf_sums[e+1] for e in range(len(self.rev_tf_sums)-1)]

    def save_revisions(self):
        with open('revisions/' + CONCEPT + '.csv', 'wb') as out:
            writer = csv.writer(out, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for rev in self.revisions:
                writer.writerow([rev['id'], rev['dt'], rev['change']])

def main():
    wikiedits = WikiEdits(data_dir=RAW_DATA_DIR)
    wikiedits.parse(CONCEPT)
    wikiedits.save_revisions()
if __name__ == '__main__':
    main()