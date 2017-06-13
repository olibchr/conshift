import json, csv, scipy, sys
from dateutil import parser as dtparser

path = '/Users/oliverbecher/1_data/0_cwi/1_data/'
#path = '/export/scratch1/home/becher/data/'

exp_file = sys.argv[1]

def read_exp_results(exp_name):
    print('Reading from disc: {}'.format(exp_name))
    exp_results = []
    with open(exp_name) as in_file:
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
                    'cosines': rv['cosines'],
                    'wkedits': rv['wkedits'],
                    'spearman': rv['spearman'],
                    'p': rv['p']
                }
            if type(result['spearman']) != int:
                err_exp.append(result)
            else: exp_formatted.append(result)
    return exp_formatted, err_exp


def extract_averages(experiment, err_exp):
    avg_spearman = sum([abs(exp['spearman']) for exp in experiment])/len(experiment)
    avg_p = sum([exp['p']for exp in experiment])
    print('Average spearman is {}, average p-value is {}'.format(avg_spearman, avg_p))
    print('Invalid experiments: {}').format(len(err_exp))

exp_results, err_exp = read_exp_results(exp_file)
extract_averages(exp_results, err_exp)