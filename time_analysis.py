
import csv
import sys
from scipy.stats import entropy
from sklearn.metrics import pairwise as pw
import string
import warnings
import time
import datetime
import ast
warnings.filterwarnings("ignore")

"""
The purpose of this program is to do an investigation of the data which was produced with the create vectors tool.
You have to specify one or several IDs of annotations to investigate about (ID mapping can be found in separate csv file,
produce by create vector tool as well)
In detail, this tool creates density distribution vectors for the specified annotations and compares them to each other
 with a KL divergence / cosine metric to measure similarity.
 All output will be printed on screen.
"""
path = sys.argv[1]
csv.field_size_limit(sys.maxsize)

q_char = '|'


def get_ctg(filters):
    filter_id_to_ctg = {}
    all_id_to_ctg = {}
    with open(path + 'annotation_to_index.csv') as annotation_dict:
        reader = csv.reader(annotation_dict, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            if int(row[1]) in filters:
                filter_id_to_ctg[int(row[1])] = row[0]
            all_id_to_ctg[int(row[1])] = row[0]
    return filter_id_to_ctg, all_id_to_ctg


def load_distr(filters):
    all_d_content = []
    with open(path + 'all_distributions_time.csv') as distr_vec:
        reader = csv.reader(distr_vec, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        all_data = []
        for row in reader:
            if int(row[0]) not in filters: continue
            all_data.append([int(row[0]),row[1:]])
    for item in all_data:
        tups = []
        for i in range(0,len(item[1])-2,2):
            tups.append((item[1][i], int(item[1][i+1])))
        all_d_content.append([item[0], tups])
    return all_d_content


def timeframes(concept, window):
    start_date = time.strptime("2014-08-13", "%Y-%m-%d")
    end_date = time.strptime("2015-08-13", "%Y-%m-%d")
    all_frames = []
    this_date = start_date
    while this_date <= end_date:
        this_date = this_date + datetime.timedelta(days=window)
        all_frames.append(this_date)
    return timeframes()


def rebuild_distr(all_d_content, vlen):
    #print all_d_content
    vlen = 111953
    all_d_vec = []
    for d_vec in all_d_content:
        d_vector = [0.000001] * vlen
        d_id = d_vec[0]
        for keyval in d_vec[1]:
            d_vector[keyval[0]] = keyval[1]
        #print "     " + str(sum(d_vector))
        all_d_vec.append([d_id, d_vector])
    return all_d_vec


# might be problem: distributions might not contain a specific vector --> need identifier
def kl_div(distr):
    all_div = []
    for i in range(0,len(distr)-1):
        this_distr = distr[i][1]
        next_distr = distr[i+1][1]
        if sum(this_distr) < 1 or sum(next_distr) < 1:
            print "Cant compare quarter " + str(i+1) + " to " + str(i+2) + ". One Vector empty: " + str(sum(this_distr)) + " or " + str(sum(next_distr))
            all_div.append('NaN')
            continue
        this_entropy = entropy(this_distr, next_distr)
        all_div.append(this_entropy)
    all_div.append(entropy(distr[0][1], distr[len(distr)-1][1]))
    return all_div


def validation_scoring(distributions):
    scoring = [0] * len(distributions)
    gold_standard = distributions[0]
    k = 0
    for d in distributions:
        for i in range(0,len(d[1])):
            if (d[1][i] >= 0.00001) and (gold_standard[1][i] >= 0.00001):
                scoring[k] += 1
        k += 1
    return scoring


def remap(distributions, filters):
    distr_per_id = []
    for i in range(0,len(filters)):
        this_dist = []
        this_dist.append(distributions[0][i])
        this_dist.append(distributions[1][i])
        this_dist.append(distributions[2][i])
        this_dist.append(distributions[3][i])
        distr_per_id.append(this_dist)
    return distr_per_id



def main(argv):
    filters = map(int, argv[2:])
    print "Setting filters.. "

    filter_id_to_ctg, all_id_to_ctg = get_ctg(filters)

    for filter in filters:
        print "     " + str(filter) + ": " + str(filter_id_to_ctg[filter].split('/')[-1])

    distributions = load_distr(filters)

    print "Create sparse vectors"
    for i in range(0,len(distributions)):
        distributions[i] = rebuild_distr(distributions[i], len(all_id_to_ctg))

    print "Built " + str(len(distributions[0])) + " probability density vectors"

    distributions = remap(distributions, filters)

    divergences_per_id = []
    for distr in distributions:
        divergences_per_id.append(kl_div(distr))
    for i in range(0,len(filters)):
        print "KL Divergences within filter " + str(filter_id_to_ctg[filters[i]].split('/')[-1]) + " are: "

        print "     Quarter 1 to Quarter 2: " + str(divergences_per_id[i][0])
        print "     Quarter 2 to Quarter 3: " + str(divergences_per_id[i][1])
        print "     Quarter 3 to Quarter 4: " + str(divergences_per_id[i][2])
        print "     Quarter 1 to Quarter 4: " + str(divergences_per_id[i][3])
        print ""

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: enter one or several indices from the dictionary hinting at wikipedia annotations which are preferably related. This program calculates the cosine similarity between the first entered index and all other entered indeces."
    else:
        main(sys.argv)
