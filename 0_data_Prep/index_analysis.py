

import csv
import sys
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy.stats import entropy
from sklearn.preprocessing import normalize
from sklearn.metrics import pairwise as pw
import wikipedia
import warnings
warnings.filterwarnings("ignore")

"""
Little tool to investigate annotations a bit more
"""
path = '/Users/oliverbecher/1_data/0_cwi/1_data/'

def get_ctg():
    all_id_to_ctg = {}
    with open(path + 'annotation_to_index.csv') as annotation_dict:
        reader = csv.reader(annotation_dict, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            all_id_to_ctg[int(row[1])] = row[0]
    # all_id_to_ctg = {int(v): k for k, v in all_id_to_ctg.iteritems()}
    return all_id_to_ctg


def get_ind_cnt():
    all_ind = []
    with open('index_cnt.csv') as ind_cnt:
        reader = csv.reader(ind_cnt, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            all_ind.append([row[0], int(row[1]), int(row[2])])
    return all_ind


def print_top_cnts():
    std = np.array(map(int, [int(row[1]) for row in all_ind]))
    print "AVG: " + str(np.average(std))
    print "StDev: " + str(np.std(std, axis=0))
    print "Top 10: "

    for i in range(0,400):
        if 'Category' in all_id_to_ctg[int(all_ind[i][0])].split('/')[-1]:
            continue
        else:
            print all_id_to_ctg[int(all_ind[i][0])].split('/')[-1] + ": " + str(all_ind[i][1]) + " hits. " + str(all_ind[i][0])

def update_ind_cnt():
    new_cnt = []
    err_list = []
    for ind in all_ind:
        if ind[0] in all_ctg_to_id:
            new_cnt.append([ind[0],all_ctg_to_id[ind[0]],ind[2]])
        else: err_list.append(ind[0])
    return sorted(new_cnt, reverse=True, key= lambda cnt:cnt[2])


def save_ind_cnt(out):
    with open('index_cnt_update.csv','w') as outfile:
        writer = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for o in out:
            writer.writerow(o)


all_id_to_ctg = get_ctg()
all_ctg_to_id = {v: int(k) for k, v in all_id_to_ctg.iteritems()}
all_ind = get_ind_cnt()
all_ind = sorted(all_ind, key=lambda entree: entree[1], reverse=True)

all_ind_update = update_ind_cnt()
save_ind_cnt(all_ind_update)





