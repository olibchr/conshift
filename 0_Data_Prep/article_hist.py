import csv, sys, matplotlib
from dateutil import parser as dtparser
import datetime, time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
path = '/Users/oliverbecher/1_data/0_cwi/1_data/'
filters = map(int, sys.argv[1:])

def load_distr():
    with open(path + 'all_distributions_time.csv') as distr_vec:
        reader = csv.reader(distr_vec, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        all_data = []
        for row in reader:
            if int(row[0]) not in filters: continue
            articles = set([int(art.split('_')[1]) for art in row[1:]])
            all_data.append([int(row[0]),articles])
            if len(all_data) == len(filters): break
    return all_data


def get_ctg():
    all_id_to_ctg = {}
    with open(path + 'annotation_to_index.csv') as annotation_dict:
        reader = csv.reader(annotation_dict, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            all_id_to_ctg[int(row[1])] = row[0]
    return all_id_to_ctg


def load_doc_map(path):
    docid_to_date = {}
    with open(path + 'docid_to_date.csv') as docmap:
        reader = csv.reader(docmap, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            docid_to_date[int(row[0])] = row[1]
    return docid_to_date


def con_docs_to_date(concepts):
    all_concepts = []
    for con in concepts:
        this_dates = []
        for d in con[1]:
            dt = dtparser.parse(docid_to_date[d])
            this_dates.append(time.mktime(dt.timetuple()))
        c = {
            'id': con[0],
            'name': all_id_to_ctg[con[0]],
            'dates': this_dates
        }
        all_concepts.append(c)
    return all_concepts


def plot_date_hists(concepts):
    for con in concepts:
        mpl_data = mdates.epoch2num(con['dates'])

        # plot it
        fig, ax = plt.subplots(1,1)
        ax.hist(mpl_data, bins=50, color='lightblue', label=con['name'])
        red_patch = mpatches.Patch(color='lightblue', label=con['name'])
        plt.legend(handles=[red_patch])

        locator = mdates.AutoDateLocator()
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(mdates.AutoDateFormatter(locator))
        plt.show()


concepts = load_distr()
all_id_to_ctg= get_ctg()
docid_to_date = load_doc_map(path)
concepts = con_docs_to_date(concepts)
plot_date_hists(concepts)
