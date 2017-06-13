import wiki_comparison
import csv, sys, random
from joblib import Parallel, delayed
import multiprocessing


path = '/Users/oliverbecher/1_data/0_cwi/1_data/'
conceptsPerRequest = 6

concepts = int(sys.argv[1])

def get_ind_cnt():
    all_ind = []
    with open('index_cnt.csv') as ind_cnt:
        reader = csv.reader(ind_cnt, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
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
    print offset1, offset2
    return offset1, offset2


def get_indeces(offset1, offset2):
    if concepts/3 > offset1: top_cnt = random.sample(xrange(concepts/3), concepts/3)
    else:
        top_cnt = random.sample(xrange(offset1), concepts/3)
    if concepts/3 > offset2: med_cnt = random.sample(xrange(concepts/3),concepts/3)
    else:
        med_cnt = random.sample(xrange(offset1, offset2), concepts/3)
    low_cnt = random.sample(xrange(offset1+offset2, 71564), concepts/3)
    all_indeces = top_cnt + med_cnt + low_cnt
    return all_indeces


def start_processes(procs):
    for proc in procs:
        proc.start()
    for proc in procs:
        proc.join()

all_ind_cnt = get_ind_cnt()
offset1, offset2 = get_ranges(all_ind_cnt)
filter_indeces = get_indeces(offset1, offset2)
filters = [all_ind_cnt[i][1] for i in filter_indeces]

filter_badges = [filters[i:i+conceptsPerRequest] for i in range(0,len(filters), conceptsPerRequest)]
print filter_badges

num_cores = multiprocessing.cpu_count()
Parallel(n_jobs=2)(delayed(wiki_comparison.experiment_1)(badge) for badge in filter_badges)


"""
procs = []
filter_offset = 0
while filter_offset < len(filters):
    print filter_offset,len(filters)
    if filter_offset+conceptsPerRequest >= len(filter_indeces): end = len(filter_indeces)
    else: end = filter_offset + conceptsPerRequest
    this_filters = filters[filter_offset:end]
    filter_offset += conceptsPerRequest
    proc = Process(target=wiki_comparison.experiment_1(this_filters))
    procs.append(proc)
    if len(procs) >= 2 or filter_offset >= len(filters):
        start_processes(procs)
    #wiki_comparison.experiment_1(this_filters)
"""
