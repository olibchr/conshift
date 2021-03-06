import json, csv, scipy, sys, math, os
from dateutil import parser as dtparser
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import scipy.stats

#path = '/Users/oliverbecher/1_data/0_cwi/1_data/'
path = '/export/scratch1/home/becher/data/'
exppath = './'

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
    with open(exppath + exp_name) as in_file:
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
                    'p': rv['p'],
                    'counts': all_ind_cnt[unicode('http://en.wikipedia.org/wiki/'+rv['concept']).encode('utf-8', 'ignore')]
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
    _, idx = max((val['spearman'], idx) for (idx, val) in enumerate(experiment))
    max_corr = experiment[idx]
    _, idx = min((val['spearman'], idx) for (idx, val) in enumerate(experiment))
    min_corr = experiment[idx]
    all_avg_cosines = [(sum(exp['cosines'])/len(exp['cosines']),idx) for (idx, exp) in enumerate(experiment)]
    max_cos = experiment[max(all_avg_cosines)[1]]
    min_cos = experiment[min(all_avg_cosines)[1]]
    print('Average absolute spearman is {}, average p-value is {}'.format(avg_spearman, avg_p))
    print('Average spearman is {}'.format(sum([exp['spearman'] for exp in experiment])/len(experiment)))
    print('Max Corr: {}'.format(max_corr['id']))
    print('Min Corr: {}'.format(min_corr['id']))
    print('Max Cos: {}'.format(max_cos['id']))
    print('Min Cos: {}'.format(min_cos['id']))
    if len(err_exp) > 0: eval_err_exps(err_exp, avg_sim)


def make_hists(exp_results):
    spearmans = [x['spearman'] for x in exp_results]
    pvals = [x['p'] for x in exp_results]
    avg_sim_p_con = [sum(exp['cosines'])/len(exp['cosines']) for exp in exp_results]
    # plot it

    fig, ax = plt.subplots(figsize=(4, 6))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()
    red_patch = mpatches.Patch(color='lightblue', label='Spearman')
    blue_patch = mpatches.Patch(color='red', label='P vals')


    ax.hist(spearmans, bins=50, color='#3F5D7D', label='Spearman')
    #plt.legend(handles=[red_patch, blue_patch])
    plt.savefig("histogram_spearmans.png", bbox_inches="tight");
    #plt.show()

    counts = [x['counts'] for x in exp_results]
    fig, ax = plt.subplots(1,1)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.scatter(avg_sim_p_con,counts)
    #plt.show()
    plt.savefig("counts.png", bbox_inches="tight");



def analyze_small_p(exp_results):
    print "\nSubsampling experiments with p < 0.05:\n"
    succ = []
    for e in exp_results:
        if e['p'] < 0.05: succ.append(e)
    make_hists(succ)
    #get_spearman(succ)
    extract_averages(succ, [])


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


def comparator(concepts_cosines, wikiedit_counts):
    #print concepts_cosines, wikiedit_counts
    corr, r_val = scipy.stats.spearmanr(concepts_cosines, wikiedit_counts)
    return corr, r_val


def get_spearman(experiments):
    cosines = [exp['cosines'] for exp in experiments]
    wp_edits = [exp['wkedits'] for exp in experiments]
    g_spear, g_p = comparator(cosines, wp_edits)
    print('Global Spearman: {}, global P Val: {}'.format(len(g_spear[0]),g_p))

all_ind_cnt = get_ind_cnt()
exp_results, err_exp = read_exp_results(exp_file)
extract_averages(exp_results, err_exp)
make_hists(exp_results)
analyze_small_p(exp_results)
#extract_filters()