import wiki_comparison
import csv, sys, random
from multiprocessing import Process

path = '/Users/oliverbecher/1_data/0_cwi/1_data/'
conceptsPerRequest = 6

concepts = sys.argv[1]

def get_ind_cnt():
    all_ind = []
    with open('index_cnt.csv') as ind_cnt:
        reader = csv.reader(ind_cnt, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            all_ind.append([row[0], int(row[1]), int(row[2])])
    return all_ind


def get_ranges(ind_cnt):
    offset1 = 0
    offset2 = 0
    for item in ind_cnt:
        if item[2] > 1000: offset1 +=1 # tbd
        if item[2] > 10: offset2 += 1 # tbd
        else: break
    return offset1, offset2


def get_indeces(offset1, offset2):
    top_cnt = random.sample(xrange(offset1), concepts/3)
    med_cnt = random.sample(xrange(offset1, offset2), concepts/3)
    low_cnt = random.sample(xrange(offset1+offset2, 71564), concepts/3)
    all_indeces = top_cnt + med_cnt + low_cnt
    return all_indeces


all_ind_cnt = get_ind_cnt()
offset1, offset2 = get_ranges(all_ind_cnt)
filter_indeces = get_indeces(offset1, offset2)
filters = [all_ind_cnt[i] for i in filter_indeces]
procs = []
print filter_indeces, filters

filter_offset = 0
while filter_offset <= len(filters):
    if filter_offset+conceptsPerRequest >= len(filter_indeces): end = len(filter_indeces)
    else: end = filter_offset + conceptsPerRequest
    this_filters = filters[filter_offset:end]
    filter_offset += conceptsPerRequest
    proc = Process(target=wiki_comparison.experiment_1(), args=this_filters)
    procs.append(proc)
    proc.start()
    #wiki_comparison.experiment_1(this_filters)
    if len(procs) >= 2:
        for pr in procs: pr.join()

