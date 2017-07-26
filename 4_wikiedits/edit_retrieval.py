import os
import sys, csv
import requests
from bs4 import BeautifulSoup
from dateutil import parser as dtparser
import pytz, io, json
import urllib2, re

START_YEAR = 2000
END_YEAR = 2018
RAW_DATA_DIR = 'wikijson'
if len(sys.argv) > 1: CONCEPT = sys.argv[1]
else: CONCEPT = 'Uber_(company)'
STARTDATE = dtparser.parse('2014-08-13T00:00:00Z')
ENDDATE = dtparser.parse('2015-08-14T00:00:00Z')

utc = pytz.UTC
def file_exists(fname):
    if os.path.isfile(fname):
        return True
    return False


def bot_list():
    with open('4_wikiedits/botlist.txt','r') as f:
        content = f.readlines()
    bots = set([x.strip() for x in content])
    return bots

def save_revs(srcfile, revisions):
    out_format = []
    for rv in revisions:
        out_format.append({'id': rv['id'],'dt':str(rv['dt'])})
    with io.open(srcfile, 'w', encoding='utf-8') as f:
        f.write(unicode(json.dumps(out_format, encoding='utf8', ensure_ascii=False)))


def read_revisions(srcfile):
    # print('Reading from disc: {}'.format(srcfile))
    with open(srcfile) as json_data:
        revisions = json.load(json_data)
    revisions_formatted = []
    for rv in revisions:
        row = {
            'id': rv['id'],
            'dt': dtparser.parse(rv['dt'])
        }
        revisions_formatted.append(dict(row))
    return revisions_formatted


def get_resource(url):
        print('Fetching: {}'.format(url))
        r = requests.get(url)
        print "Resource obtained"
        if r.status_code != 200:
            print('Error: {}.'.format(r.status_code))
        return r

def GetRevisions(pageTitle):
    url = "https://en.wikipedia.org/w/api.php?action=query&format=xml&prop=revisions&rvlimit=500&titles=" + pageTitle
    revisions = []                                        #list of all accumulated revisions
    next = ''                                             #information for the next request
    while True:
        response = urllib2.urlopen(url + next).read()     #web request
        revisions += re.findall('<rev [^>]*>', response)  #adds all revisions from the current request to the list
        cont = re.search('<continue rvcontinue="([^"]+)"', response)
        if not cont:                                      #break the loop if 'continue' element missing
            break
        next = "&rvcontinue=" + cont.group(1)             #gets the revision Id from which to start the next requst
    return revisions


class WikiEdits:
    def __init__(self, data_dir='wikijson'):
        self.base_url = 'https://en.wikipedia.org/wiki/Special:Export/'
        self.data_dir = data_dir
        # print self.data_dir
    def get_history(self, title):
        #url = '{}{}?history'.format(self.base_url, title)
        #r = get_resource(url)
        #return r.content
        r = '<revisions>' + ''.join(GetRevisions(title)) + '</revisions'
        return r

    def parse(self, title, refresh=False):
        self.revisions = []
        srcfile = '{}/{}.json'.format(self.data_dir, title.lower())
        if file_exists(srcfile) and refresh==False:
            self.revisions = read_revisions(srcfile)
        else:
            bots = bot_list()
            txt = self.get_history(title)
            #print 'Parsing ...'
            soup = BeautifulSoup(txt, 'lxml-xml')
            #print 'Finding revisions ...'
            revisions = soup.find_all('rev')

            for i, rev in enumerate(revisions):
                if 'user' in rev:
                    if rev['user'] in bots: print "bot detected"; continue
                row = {
                    'id':rev['revid'],
                    'dt':dtparser.parse(rev['timestamp'])
                }
                if row['dt'] > ENDDATE: continue
                if row['dt'] < STARTDATE: continue
                self.revisions.append(dict(row))
            save_revs(srcfile, self.revisions)
        if len(self.revisions) <= 1:
            txt = self.get_history(title)
            print 'Parsing ...'
            soup = BeautifulSoup(txt, 'lxml-xml')
            print 'Finding revisions ...'
            revisions = soup.find_all('rev')

            for i, rev in enumerate(revisions):
                row = {
                    'id':rev['revid'],
                    'dt':dtparser.parse(rev['timestamp'])
                }
                if row['dt'] > ENDDATE: continue
                if row['dt'] < STARTDATE: continue
                self.revisions.append(dict(row))
            save_revs(srcfile, self.revisions)
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
                writer.writerow([rev['id'], rev['dt']])

def main():
    wikiedits = WikiEdits(data_dir=RAW_DATA_DIR)
    wikiedits.parse(CONCEPT, refresh=True)
    wikiedits.save_revisions()

if __name__ == '__main__':
    main()