import wiki_comparison
import csv, sys, random
from joblib import Parallel, delayed
import multiprocessing


#path = '/Users/oliverbecher/1_data/0_cwi/1_data/'
path = '/export/scratch1/home/becher/data/'
conceptsPerRequest = 30

num_concepts = int(sys.argv[2])
num_cores = multiprocessing.cpu_count()


def get_ind_cnt():
    all_ind = []
    all_ind_dt = dict()
    with open(path + 'index_cnt.csv') as ind_cnt:
        reader = csv.reader(ind_cnt, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            all_ind.append([row[0], int(row[1]), int(row[2])])
            all_ind_dt[int(row[1])] = int(row[2])
    return all_ind, all_ind_dt


def get_ranges(ind_cnt):
    offset1 = 0
    offset2 = 0
    offset3 = 0
    for item in ind_cnt:
        if item[2] > 1000: offset1 += 1 # tbd
        if item[2] > 100: offset2 += 1
        if item[2] > 11: offset3 += 1 # tbd
        else: break
    print offset1, offset2, offset3
    return offset1, offset2, offset3


def stratefied_sample(offset1, offset2, offset3):
    if num_concepts/3 > offset1: top_cnt = random.sample(xrange(num_concepts / 3), num_concepts / 3)
    else:
        top_cnt = random.sample(xrange(offset1), num_concepts / 3)
    if num_concepts/3 > offset2: med_cnt = random.sample(xrange(num_concepts / 3), num_concepts / 3)
    else:
        med_cnt = random.sample(xrange(offset1, offset2), num_concepts / 3)
    low_cnt = random.sample(xrange(offset2, offset3), num_concepts / 3)
    all_indeces = top_cnt + med_cnt + low_cnt
    return all_indeces


def get_filter_badges():
    all_ind_cnt, all_ind_dt = get_ind_cnt()
    offset1, offset2, offset3 = get_ranges(all_ind_cnt)
    filter_indeces = stratefied_sample(offset1, offset2, offset3)
    filters = [all_ind_cnt[i][1] for i in filter_indeces]
    return [filters[i:i+conceptsPerRequest] for i in range(0,len(filters), conceptsPerRequest)]


def filter_badges_24():
    all_ind_cnt, all_ind_dt = get_ind_cnt()
    with open(path + 'filter_subset', 'r') as in_file:
        subset = map(int, in_file.read().split(', '))
    for f in subset:
        if all_ind_dt[f] < 24: subset.pop(subset.index(f))
    rand_smpl = [ subset[i] for i in sorted(random.sample(xrange(len(subset)), num_concepts)) ]
    return [rand_smpl[i:i+conceptsPerRequest] for i in range(0,len(rand_smpl), conceptsPerRequest)]


def exp1():
    print 'Experiment 1'
    filter_badges = get_filter_badges()
    print filter_badges
    Parallel(n_jobs=num_cores/2)(delayed(wiki_comparison.experiment_1)(badge, path) for badge in filter_badges)


def exp2():
    filter_badges = get_filter_badges()
    print 'Experiment 2'
    print filter_badges
    Parallel(n_jobs=num_cores/2)(delayed(wiki_comparison.experiment_2)(badge, path, 12) for badge in filter_badges)


def exp3():
    filter_badges = get_filter_badges()
    print 'Experiment 3'
    print filter_badges
    Parallel(n_jobs=num_cores/2)(delayed(wiki_comparison.experiment_3)(badge, path) for badge in filter_badges)


def exp4():
    filter_badges = filter_badges_24()
    print 'Experiment 4'
    print filter_badges
    Parallel(n_jobs=num_cores/2)(delayed(wiki_comparison.experiment_4)(badge, path, 24) for badge in filter_badges)
    Parallel(n_jobs=num_cores/2)(delayed(wiki_comparison.experiment_4)(badge, path, 12) for badge in filter_badges)
    Parallel(n_jobs=num_cores/2)(delayed(wiki_comparison.experiment_4)(badge, path, 6) for badge in filter_badges)
    Parallel(n_jobs=num_cores/2)(delayed(wiki_comparison.experiment_4)(badge, path, 4) for badge in filter_badges)


def exp5():
    filter_badges = filter_badges_24()
    print 'Experiment 5'
    print filter_badges
    Parallel(n_jobs=num_cores/2)(delayed(wiki_comparison.experiment_2)(badge, path, 24) for badge in filter_badges)
    Parallel(n_jobs=num_cores/2)(delayed(wiki_comparison.experiment_2)(badge, path, 12) for badge in filter_badges)
    Parallel(n_jobs=num_cores/2)(delayed(wiki_comparison.experiment_2)(badge, path, 6) for badge in filter_badges)
    Parallel(n_jobs=num_cores/2)(delayed(wiki_comparison.experiment_2)(badge, path, 4) for badge in filter_badges)


if sys.argv[1] == '1':
    exp1()
if sys.argv[1] == '2':
    exp2()
if sys.argv[1] == '3':
    exp3()
if sys.argv[1] == '4':
    exp4()
if sys.argv[1] == '5':
    exp5()