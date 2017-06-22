import json, csv, scipy, sys, math, os
from dateutil import parser as dtparser

#path = '/Users/oliverbecher/1_data/0_cwi/1_data/'
#path = '/export/scratch1/home/becher/data/'
path = './'

exp_file = sys.argv[1]

def get_ind_cnt():
    all_ind = dict()
    with open(path + 'index_cnt.csv') as ind_cnt:
        reader = csv.reader(ind_cnt, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            all_ind[row[0]] = int(row[2])
    return all_ind

def read_exp_results(exp_name):
    print('Reading from disc: {}'.format(exp_name))
    exp_results = []
    with open(path + exp_name) as in_file:
        for line in in_file:
            exp_results.append(json.loads(line))
    exp_formatted = []
    err_exp = []
    for nest_exp in exp_results:
        for rv in nest_exp:
            result = {
                    'concept': rv['concept'],
                    'id': rv['id'],
                    'intervals': [dtparser.parse(dt) for dt in rv['intervals']],
                    'cosines': rv['kl_div'],
                    'wkedits': rv['wkedits'],
                    'spearman': rv['spearman'],
                    'p': rv['p']
                }
            if type(result['spearman']) != float or math.isnan(result['spearman']):
                err_exp.append(result)
            else: exp_formatted.append(result)
    return exp_formatted, err_exp


def eval_err_exps(err_exps, avg_cosim):
    avg_err_cosines =[]
    strati_high_cnt = 0
    strati_med_cnt = 0
    strati_low_cnt = 0
    for exp in err_exps:
        this_avg_cosim = sum([cosine for cosine in exp['cosines']])/len(exp['cosines'])
        avg_err_cosines.append(this_avg_cosim)
        name = unicode("http://en.wikipedia.org/wiki/" + exp['concept']).encode('utf8')
        if all_ind_cnt[name] > 1000: strati_high_cnt += 1
        elif all_ind_cnt[name] > 11: strati_med_cnt += 1
        else: strati_low_cnt += 1

    print("Average cosine for failed experiments: {}. Average cosine for correct experiments: {}".format(sum(avg_err_cosines)/len(avg_err_cosines), avg_cosim))
    print("Failed experiments distribution: High strati group: {}, Med strati group: {}, Low strati group: {}".format(strati_high_cnt, strati_med_cnt, strati_low_cnt))


def extract_averages(experiment, err_exp):
    print('Correct experiments: {}').format(len(experiment))
    print('Invalid experiments: {}').format(len(err_exp))
    avg_spearman = sum([abs(exp['spearman']) for exp in experiment])/len(experiment)
    avg_p = sum([exp['p']for exp in experiment])/len(experiment)
    avg_sim = sum([sum(exp['cosines'])/len(exp['cosines']) for exp in experiment])/len(experiment)
    print('Average spearman is {}, average p-value is {}'.format(avg_spearman, avg_p))
    eval_err_exps(err_exp, avg_sim)


def extract_filters():
    all_exps, all_err_exps = [], []
    for filename in os.listdir(path):
        if ".json" not in filename:
            continue
        exp, err_exp = read_exp_results(filename)
        all_exps = all_exps + exp
        all_err_exps = all_err_exps + err_exp

    all_ids = []
    for exp in all_exps:
        all_ids.append(exp['id'])
    for exp in all_err_exps:
        all_ids.append(exp['id'])
    all_ids = set(all_ids)
    print all_ids

all_ind_cnt = get_ind_cnt()
exp_results, err_exp = read_exp_results(exp_file)
extract_averages(exp_results, err_exp)
#extract_filters()