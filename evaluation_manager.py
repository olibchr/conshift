import wiki_comparison
import csv, sys, random
from joblib import Parallel, delayed
import multiprocessing


path = '/Users/oliverbecher/1_data/0_cwi/1_data/'
#path = '/export/scratch1/home/becher/data/'
conceptsPerRequest = 3

num_concepts = int(sys.argv[1])


def get_ind_cnt():
    all_ind = []
    with open(path + 'index_cnt.csv') as ind_cnt:
        reader = csv.reader(ind_cnt, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            all_ind.append([row[0], int(row[1]), int(row[2])])
    return all_ind


def get_ranges(ind_cnt):
    offset1 = 0
    offset2 = 0
    for item in ind_cnt:
        if item[2] > 1000: offset1 +=1 # tbd
        if item[2] > 11: offset2 += 1 # tbd
        else: break
    print offset1, offset2
    return offset1, offset2


def get_indeces(offset1, offset2):
    if num_concepts/3 > offset1: top_cnt = random.sample(xrange(num_concepts / 3), num_concepts / 3)
    else:
        top_cnt = random.sample(xrange(offset1), num_concepts / 3)
    if num_concepts/3 > offset2: med_cnt = random.sample(xrange(num_concepts / 3), num_concepts / 3)
    else:
        med_cnt = random.sample(xrange(offset1, offset2), num_concepts / 3)
    low_cnt = random.sample(xrange(offset1+offset2, 71564), num_concepts / 3)
    all_indeces = top_cnt + med_cnt + low_cnt
    return all_indeces


def get_indeces_exp2(offset1, offset2):
    if num_concepts/3 > offset1: top_cnt = random.sample(xrange(num_concepts / 3), num_concepts / 3)
    else:
        top_cnt = random.sample(xrange(offset1), num_concepts / 3)
    if num_concepts/3 > offset2: med_cnt = random.sample(xrange((2*num_concepts) / 3), (2*num_concepts) / 3)
    else:
        med_cnt = random.sample(xrange(offset1, offset2), (2*num_concepts) / 3)
    all_indeces = top_cnt + med_cnt
    return all_indeces


all_ind_cnt = get_ind_cnt()
offset1, offset2 = get_ranges(all_ind_cnt)
#filter_indeces = get_indeces(offset1, offset2)
filter_indeces = get_indeces_exp2(offset1, offset2)
filters = [all_ind_cnt[i][1] for i in filter_indeces]

filter_badges = [filters[i:i+conceptsPerRequest] for i in range(0,len(filters), conceptsPerRequest)]
print filter_badges

num_cores = multiprocessing.cpu_count()

# Experiment 1
#Parallel(n_jobs=num_cores/2)(delayed(wiki_comparison.experiment_1)(badge, path) for badge in filter_badges)

# Experiment 2
Parallel(n_jobs=num_cores/2)(delayed(wiki_comparison.experiment_2)(badge, path) for badge in filter_badges)

# Experiment 3
#Parallel(n_jobs=num_cores/2)(delayed(wiki_comparison.experiment_3)(badge, path) for badge in filter_badges)